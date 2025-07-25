from typing import List, Optional, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from IPython.display import Image, display
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.constants import Send

from operator import add
from langgraph_dma.utils import RealTimeDataLogs    
from langgraph_dma.personas import ITSupport
from agent.interview.state import build_interview_state



# Entry Graph
# class EntryGraphState(TypedDict):
#     raw_data: List[RealTimeDataLogs]
#     clean_data: List[RealTimeDataLogs]
#     analyst: ITSupport


class ResearchGraphState(TypedDict):
    raw_data: List[RealTimeDataLogs]
    clean_data: List[RealTimeDataLogs]
    topic: str # Research topic
    # analysts: List[ITSupport] # Analyst asking questions
    summary: str
    final_report: str # Final report


def read(state):
    raw_data = state["raw_data"]
    '''
    processing ...
    '''
    clean_data = raw_data
    print('Cleaning data ...')
    print(clean_data)
    return {"clean_data": clean_data}

# def initiate_all_interviews(state: ResearchGraphState):
#     """ This is the "map" step where we run each interview sub-graph using Send API """    
#     # Otherwise kick off interviews in parallel via Send() API

#     topic = state["topic"]
#     return [
#         Send(
#             "conduct_interview", 
#             {
#                 "analyst": analyst, 
#                 "messages": [HumanMessage(content=f"So you said you were writing an article on {topic}?")]
#             }
#         ) for analyst in state["analysts"]
#     ]


def finalize_report(state: ResearchGraphState):
    """ Finalize the report by combining all sections """
    sections = state["summary"]
    # Combine all sections into a final report
    final_report = "\n\n".join(sections)
    return {"final_report": final_report}

def build_agent():
    builder = StateGraph(ResearchGraphState)
    builder.add_node("clean_data", read) # returns clean_data
    builder.add_node("conduct_interview", build_interview_state().compile())
    builder.add_node("finalize_report",finalize_report)

    # Flow
    builder.add_edge(START, "clean_data")
    builder.add_edge("clean_data", "conduct_interview")
    builder.add_edge("conduct_interview", "finalize_report")
    builder.add_edge("finalize_report", END)
    return builder


# graph = builder.compile()

# from IPython.display import Image, display
# img = graph.get_graph(xray=1).draw_mermaid_png()
# with open("graph.png", "wb") as f:
#     f.write(img)
# import os
# os.system("open graph.png")


