from langgraph.graph import START, END, StateGraph,MessagesState
from langchain_core.messages import  SystemMessage, HumanMessage, AIMessage
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
from operator import add
from typing import List, Optional, Annotated
from langgraph_dma.personas import ITSupport
from langgraph_dma.llm import OPENAILLM
from langgraph_dma.tools import tool_read_etl_job_status
import datetime
from pydantic import BaseModel
import logging
import json 



# For this ipynb we set parallel tool calling to false as math generally is done sequentially, and this time we have 3 tools that can do math
# the OpenAI model specifically defaults to parallel tool calling for efficiency, see https://python.langchain.com/docs/how_to/tool_calling_parallel/
# play around with it and see how the model behaves with math equations!
tools = [tool_read_etl_job_status]
TLLM = OPENAILLM.bind_tools(tools, parallel_tool_calls=False)

JOBS = [
    {
        "id": "job1",
        "url": "https://example.com/job1",
        "tags": ['WIND_SPEED'],
        "assets": ['ASSET3', 'ASSET4'],
    },
    {
        "id": "job2",
        "url": "https://example.com/job2",
        "tags": ['WIND_SPEED'],
        "assets": ['ASSET2'],
    },
    {
        "id": "job3",
        "url": "https://example.com/job3",
        "tags": ['POWER'],
        "assets": ['ASSET1'],
    },
    {
        "id": "job4",
        "url": "https://example.com/job4",
        "tags": ['IRRADIATION'],
        "assets": ['ASSET56'],
    }
]

class ETLJobState(MessagesState):
    rejected_data: List[str]
    jobs: list[dict]
    update: list[dict]


JOB_STATUS_INSTRUCTIONS = """
    ## Improved Prompt for Data Validation
    You are a meticulous Data Quality Analyst. 
    Your sole purpose is to validate a given rejected data and check its corresponding ETL job based on
    what tags and assets these jobs processing. Use a job id as a parameter to check etl status.
    Ignore any jobs that are not relevant to the rejected data.

    ## Instructions
    By using provided jobs that are currently running on production, read status of each etl job.

    If a job is running, you should highlight its status as "running" for a given data.
    If a job has failed, you should highlight its status as "failed" and provide the error message.

"""

def input_context(state: ETLJobState):
    return {
        "jobs": JOBS,
        "rejected_data": state["rejected_data"]
    }

def check_etl_status(state: ETLJobState):
    """ Node to answer a question """
    
    jobs = state["jobs"]
    system_message = JOB_STATUS_INSTRUCTIONS

    return {
        "messages": TLLM.invoke(
            [SystemMessage(content=system_message)] + state['messages'] + 
            [HumanMessage(content=f"Check the status of the following jobs: {jobs}")]
        )
    }
    

UPDATE_STATUS_INSTRUCTIONS = """    
    ## Improved Prompt for Data Validation
    You are a meticulous Data Analyst Support. 
    Your sole purpose is to validate a given jobs status and provide an update.

    ## Instructions
    By using provided context, generate update report on rejected data and jobs associated with them.
    Provide a concise summary of the status of each job, including any errors or issues that need to be addressed.
"""

def get_status_update(state: ETLJobState):
    """ Extracts the rejected data from the analysis results """

    status_update = OPENAILLM.invoke(
        [SystemMessage(content=UPDATE_STATUS_INSTRUCTIONS)]
    )
    return {"update": status_update.content}
    


def build_etl_status_graph():
    # Add nodes and edges 
    builder = StateGraph(ETLJobState)
    builder.add_node("input_context", input_context)
    builder.add_node("check_etl_status", check_etl_status)
    builder.add_node("tools", ToolNode(tools))
    builder.add_node("get_status_update", get_status_update)
    # Flow
    builder.add_edge(START, "input_context")
    builder.add_edge("input_context", "check_etl_status")
    builder.add_conditional_edges(
        "check_etl_status",
        # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
        # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
        tools_condition,
    )
    builder.add_edge("tools", "check_etl_status")
    builder.add_edge("check_etl_status", "get_status_update")
    builder.add_edge("get_status_update", END)
    return builder


'''

{"tools": "tools", "__end__": "process_tool_results"}
builder.add_conditional_edges(
    "check_etl_status",
    tools_condition,
    {"tools": "tools", "__end__": "process_tool_results"}
)

 you want to execute the tool calls first and use its results in next node

'''