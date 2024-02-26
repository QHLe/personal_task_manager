#%% Create tools

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool

class SearchInput(BaseModel):
    query: str = Field(description="should be a search query")


@tool("search-tool", args_schema=SearchInput, return_direct=True)
def search(query: str) -> str:
    """Look up things online."""
    return "LangChain"

@tool
def low_letters(input_string: str) -> str:
    '''search online for the weather data of a city '''
    return input_string.lower()

# %% Convert to openai compatible tools

from langchain_core.utils.function_calling import convert_to_openai_function

tools = [low_letters, search]
functions = [convert_to_openai_function(t) for t in tools]

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
result = model.invoke("how is the weather today in Friedrichshafen Germany?")

# Print the result
print(result)

#%% Use the LLM response to call the tool
from langgraph.prebuilt import ToolInvocation
from langgraph.prebuilt import ToolExecutor
import json

tool_executor = ToolExecutor(tools)

action = ToolInvocation(
        tool=result.additional_kwargs["function_call"]["name"],
        tool_input=json.loads(
            result.additional_kwargs["function_call"]["arguments"]
        ),
    )

print(action)
print(tool_executor.invoke(action))

# %% Call the model and execute the tool at once

