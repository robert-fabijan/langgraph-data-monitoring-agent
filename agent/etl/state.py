from langgraph.graph import START, END, StateGraph,MessagesState
from langchain_core.messages import  SystemMessage, HumanMessage
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
from operator import add
from typing import List, Optional, Annotated
from langgraph_dma.personas import ITSupport
from langgraph_dma.llm import OPENAILLM
from langgraph_dma.utils import tool_read_etl_job_status
import datetime
from pydantic import BaseModel
import logging
import json 

class ETLJob(BaseModel):
    id: str
    status: str
    error: Optional[str] = None
    timestamp: datetime.datetime


class ETLJobState(MessagesState):
    rejected_data: List[str]
    jobs: list[ETLJob]
    update: str

# For this ipynb we set parallel tool calling to false as math generally is done sequentially, and this time we have 3 tools that can do math
# the OpenAI model specifically defaults to parallel tool calling for efficiency, see https://python.langchain.com/docs/how_to/tool_calling_parallel/
# play around with it and see how the model behaves with math equations!
tools = [tool_read_etl_job_status]
TLLM = OPENAILLM.bind_tools(tools, parallel_tool_calls=False)

JOBS = [
    {
        "id": "job1",
        "url": "https://example.com/job1",
    },
    {
        "id": "job2",
        "url": "https://example.com/job2",
    },
    {
        "id": "job3",
        "url": "https://example.com/job3",
    }
]

SCHEMA = ETLJob.schema_json(indent=2)

JOB_STATUS_INSTRUCTIONS = """
    ## Improved Prompt for Data Validation
    You are a meticulous Data Quality Analyst. 
    Your sole purpose is to validate a given data and check its corresponding ETL job.

    ## Instructions
    By using provided jobs that are currently running, check the status of each job.
    Final format of your response should match the following schema:
    {SCHEMA}

    If a job is running, you should return its status as "running".
    If a job has failed, you should return its status as "failed" and provide the error message.
    

    JOB LIST: 
    -#-#-#-
    {JOBS}
    -#-#-#-

    DATA;
    -#-#-#-
    {DATA}
    -#-#-#-
"""

def check_etl_status(state: ETLJobState):
    """ Node to answer a question """

    rejected_data = state["rejected_data"]

    system_message = JOB_STATUS_INSTRUCTIONS.format(
        SCHEMA=SCHEMA,
        JOBS=JOBS,
        DATA=json.dumps(rejected_data, indent=2)
    )
   
    results = TLLM.invoke(
        [SystemMessage(content=system_message)] + 
        [HumanMessage(content=f"Check data status of all ETL jobs")]
    )

    try:
        job_status_list = [
            ETLJob(id=job["id"], status=job["status"], error=job.get("error"), timestamp=datetime.datetime.fromisoformat(job["timestamp"]))
            for job in json.loads(results.content)
        ]
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logging.error(f"Failed to parse LLM response: {e}")
        return {"jobs": []}
    

UPDATE_STATUS_INSTRUCTIONS = """    
    ## Improved Prompt for Data Validation
    You are a meticulous Data Quality Analyst. 
    Your sole purpose is to validate a given jobs status and provide an update.

    ## Instructions
    By using provided jobs that are currently running, check the status of each job.
    Final format of your response should be concise and human readable with listed jobs that 
    are not running or have failed. Add exact cause of error and propose a solution to fix it.
"""

def get_status_update(state: ETLJobState):
    """ Extracts the rejected data from the analysis results """

    status_update = OPENAILLM.invoke(
        [SystemMessage(content=UPDATE_STATUS_INSTRUCTIONS)] +
        [HumanMessage(content=f"Is everything ok with our ETL jobs?")]
    )
    return {"update": status_update.content}
    


def build_etl_status_graph():
    # Add nodes and edges 
    builder = StateGraph(ETLJobState)
    builder.add_node("check_etl_status", check_etl_status)
    builder.add_node("tools", ToolNode(tools))
    builder.add_node("get_status_update", get_status_update)
    # Flow
    builder.add_edge(START, "check_etl_status")
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

