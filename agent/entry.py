from typing import List, Optional, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from IPython.display import Image, display
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.constants import Send

from operator import add
from langgraph_dma.utils import RealTimeDataLogs    
from langgraph_dma.personas import ITSupport
from agent.interview.state import build_interview_graph
from agent.etl.state import build_etl_status_graph

RULES = [
    "Data must not contain more than 3 null occurences",
    "Data latency between end time and capture time must not exceed 60 seconds",
]



class ResearchGraphState(MessagesState):
    raw_data: List[RealTimeDataLogs]
    rules: List[str]
    clean_data: List[RealTimeDataLogs]
    rejected_data: List[str]
    update: List[str]
    final_report: str


def read(state: ResearchGraphState):
    raw_data = state["raw_data"]
    '''
    processing ...
    '''
    clean_data = raw_data
    print('Cleaning data ...')
    print(clean_data)
    return {
        "clean_data": clean_data,
        "rules" : RULES,
    }


def finalize_report(state: ResearchGraphState):
    """ Finalize the report by combining all sections """
    sections = state["update"]
    return {"final_report": sections}

def build_agent():
    builder = StateGraph(ResearchGraphState)
    builder.add_node("clean_data", read)
    builder.add_node("conduct_interview", build_interview_graph().compile())
    builder.add_node("check_etl_status", build_etl_status_graph().compile())
    builder.add_node("finalize_report",finalize_report)

    # Flow
    builder.add_edge(START, "clean_data")
    builder.add_edge("clean_data", "conduct_interview")
    builder.add_edge("conduct_interview", "check_etl_status")
    builder.add_edge("check_etl_status", "finalize_report")
    builder.add_edge("finalize_report", END)
    return builder


# graph = builder.compile()

# from IPython.display import Image, display
# img = graph.get_graph(xray=1).draw_mermaid_png()
# with open("graph.png", "wb") as f:
#     f.write(img)
# import os
# os.system("open graph.png")


