#%%
import os
import json

# Load user credentials from a JSON file
with open('config.json') as json_data_file:
    data = json.load(json_data_file)

os.environ["LANGCHAIN_API_KEY"] = data["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_TRACING_V2"] = "True"
os.environ["LANGCHAIN_PROJECT"]="Langgraph"

import json
from unicodedata import category
from caldav import DAVClient, objects
import vobject

# Load user credentials from a JSON file
with open('config.json') as json_data_file:
    data = json.load(json_data_file)

# Connect to the CalDAV server
client = DAVClient(url=data["caldav_url"], username=data["username"], password=data["password"], ssl_verify_cert=False)

#%% Create tools
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool

class schema_caldav_task_mod(BaseModel):
    task_number: int = Field(description="Index to identify a specific task from the todo list, which need to be updated")
    properties: dict = Field(description="A dictionary of all to-be-changed properties and their values")


@tool("modify_task", args_schema=schema_caldav_task_mod, return_direct=True)
def modify_task(num:int, properties:dict) -> bool:
    """Update an existing task of the todo list"""
    print(properties)
    return True

class schema_caldav_task_cre(BaseModel):
    properties: dict = Field(description="""{
    "class": "optional - classification if the task is confidencial or not",
    "description": "mandatory - short description or list of subtasks written in markdown format",
    "priority": "optional - 1 to 5. 1 is the highest priority",
    "due": "optional - use the following format 2023-10-04 14:33:05+00:00",
    "summary":"mandatory - this is the title of the task. Use a meaningful name"
}""")

@tool("create_todo_task", args_schema=schema_caldav_task_cre, return_direct=True)
def modify_task(properties:dict) -> bool:
    """Create a new task on the todo list"""
    print(properties)
    return True

@tool
def get_todo_list(list_name:str) -> list:
    """Get all open task from the todo list"""
    client = DAVClient(url=data["caldav_url"], username=data["username"], password=data["password"], ssl_verify_cert=False)

    # Get the principal
    principal = client.principal()

    # Get the calendars
    calendars = principal.calendars()

    for calendar in calendars: 
        if calendar.name == 'Todo':
            task_list = calendar

    tasks = task_list.todos()

    return tasks[1]

from datetime import date
@tool
def get_date_today() -> str:
    """provide the current date as iso format"""
    return date.today().strftime('%A') + ' ' + date.today().isoformat()

@tool
def final_answer(response:str) -> str:
    """Use this tool to provide your answer to the user if you have the final answer"""
    return response

from langchain_experimental.utilities import PythonREPL
from langchain.agents import Tool

python_repl = PythonREPL()

@tool
def repl_tool(codestring:str, filename:str) -> str:
    "A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`."
    save_to_file(codestring, filename)
    return python_repl.run(codestring)


def save_to_file(text:str, filename:str) -> str:
# Open the file in write mode ('w')
    with open(filename, 'w') as f:
        # Write the string to the file
        f.write(text)
    return "sucessfully save to " + filename

from langchain_core.utils.function_calling import convert_to_openai_function

tools = [get_todo_list, modify_task, final_answer, repl_tool]
functions = [convert_to_openai_function(t) for t in tools]

from langgraph.prebuilt import ToolExecutor

tool_executor = ToolExecutor(tools)

# %% Define an LLM --> Ollama 
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler 

model = OllamaFunctions(model="codellama",
                        temperature= 0.0,
                        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()]))

# Bind the function to the model
model = model.bind(functions=functions)

# Define Agent state
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# Define Nodes

from langgraph.prebuilt import ToolInvocation
import json
from langchain_core.messages import FunctionMessage

# Define the function that determines whether to continue or not
def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    # If there is no function call, then we finish
    if last_message.additional_kwargs["function_call"]["name"] == final_answer:
        return "end"
    # Otherwise if there is, we continue
    else:
        return "continue"

# Define the function that calls the model
def call_model(state):
    messages = state["messages"]
    print(messages)
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


# Define the function to execute tools
def call_tool(state):
    messages = state["messages"]
    print(messages)
    # Based on the continue condition
    # we know the last message involves a function call
    last_message = messages[-1]
    # We construct an ToolInvocation from the function_call
    action = ToolInvocation(
        tool=last_message.additional_kwargs["function_call"]["name"],
        tool_input=json.loads(
            last_message.additional_kwargs["function_call"]["arguments"]
        ),
    )
    # We call the tool_executor and get back a response
    response = tool_executor.invoke(action)
    # We use the response to create a FunctionMessage
    function_message = FunctionMessage(content=str(response), name=action.tool)
    # We return a list, because this will get added to the existing list
    return {"messages": [function_message]}

from langgraph.graph import StateGraph, END

# Define a new graph
workflow = StateGraph(AgentState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
    # Finally we pass in a mapping.
    # The keys are strings, and the values are other nodes.
    # END is a special node marking that the graph should finish.
    # What will happen is we will call `should_continue`, and then the output of that
    # will be matched against the keys in this mapping.
    # Based on which one it matches, that node will then be called.
    {
        # If `tools`, then we call the tool node.
        "continue": "action",
        # Otherwise we finish.
        "end": END,
    },
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("action", "agent")

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
app = workflow.compile()

from langchain_core.messages import HumanMessage

inputs = {"messages": [HumanMessage(content="do I have any open tasks?")]}
app.invoke(inputs)