#%%
import os
import json

# Load user credentials from a JSON file
with open('config.json') as json_data_file:
    data = json.load(json_data_file)

os.environ["LANGCHAIN_API_KEY"] = data["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_PROJECT"]=data["LANGCHAIN_PROJECT_NAME"]

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

    return tasks

from datetime import date
@tool
def get_date_today() -> str:
    """provide the current date as iso format"""
    return date.today().strftime('%A') + ' ' + date.today().isoformat()

@tool
def default_tool(response:str) -> str:
    """Use this tool to provide your answer to the user if none of the other tools are appropriate. Your response will be directly forwarded"""
    return response

from langchain_experimental.utilities import PythonREPL
from langchain.agents import Tool

python_repl = PythonREPL()

repl_tool = Tool(
    name="python_repl",
    description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
    func=python_repl.run,
)

from langchain_core.utils.function_calling import convert_to_openai_function

tools = [get_todo_list, modify_task, default_tool, repl_tool]
functions = [convert_to_openai_function(t) for t in tools]

tools

# %% Define an LLM --> Ollama 
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler 

model = OllamaFunctions(model="codellama",
                        temperature= 0.0,
                        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()]))

# Bind the function to the model
model = model.bind(functions=functions)

#%% Execution
result = model.invoke("""You are an agent designed to write and execute python code to answer questions.
You have access to a python REPL, which you can use to execute python code.
If you get an error, debug your code and try again.
Only use the output of your code to answer the question. 
You might know the answer without running any code, but you should still run the code to get the answer.
If it does not seem like you can write code to answer the question, just return "I don't know" as the answer.
what is the date of next saturday?
""")

# Print the result
#print(result)

#%% Use the LLM response to call the tool

from langgraph.prebuilt import ToolInvocation
from langgraph.prebuilt import ToolExecutor
import json

tool_executor = ToolExecutor(tools)

action = ToolInvocation(
        tool=result.additional_kwargs["function_call"]["name"],
        tool_input=json.loads(
            result.additional_kwargs["function_call"]["arguments"]
    )
)

print(action)
result = tool_executor.invoke(action)
print(result)


# from langchain import hub
# from langchain.agents import AgentExecutor, create_openai_functions_agent

# prompt = hub.pull("hwchase17/openai-functions-agent")
#%%
# agent = create_openai_functions_agent(model, tools, prompt)

# agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
# agent_executor.invoke({"input": "Hi My name is David, how are you?"})