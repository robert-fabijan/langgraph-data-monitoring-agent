from langgraph.graph import START, END, StateGraph,MessagesState
from langchain_core.messages import  SystemMessage, HumanMessage
from operator import add
from typing import List, Optional, Annotated
from langgraph_dma.personas import ITSupport
from langgraph_dma.llm import OPENAILLM
import logging

# persona = ITSupport(
#     affiliation="Tech Support",
#     name="Alex",
#     role="IT Support Analyst",
#     description="""
#         Responsible for monitoring and analyzing data quality for a specific system or asset.
#         Focuses on assessing the health and reliability of data, identifying issues.
#         Providing actionable insights from an IT support perspective.
#     """
# )

class AnalysisState(MessagesState):
    max_num_turns: int
    context: Annotated[list, add]
    clean_data: List[str]
    rules: List[str]
    analysis: str
    rejected_data: List[str]


ANALYSIS_INSTRUCTION = """
    ## Improved Prompt for Data Validation
    You are a meticulous Data Quality Analyst. Your sole purpose is to validate a given dataset against a set of predefined rules.

    ## Instructions
    Analyze the provided `DATA` against each condition listed in the `RULES`.

    Identify every specific violation where the data does not meet a rule.

    Report your findings as a concise, bulleted list of violations. For each rule, list out the specific data points that violate it.

    If no violations are found, you MUST respond with the exact phrase: `No validation errors detected`.

    Do not add any extra explanations, greetings, or sign-offs. Go straight to the report.

    DATA: 
    -#-#-#-
    {DATA}
    -#-#-#-

    RULES:
    -#-#-#-
    {RULES}
    -#-#-#-
"""




def analyse_data(state: AnalysisState):
    """ Node to answer a question """
   
    system_message = ANALYSIS_INSTRUCTION.format(
        DATA = state["clean_data"],
        RULES = state["rules"]
    )
    analysis_results = OPENAILLM.invoke(
        [SystemMessage(content=system_message)] + 
        [HumanMessage(content=f"Does the provided data look good?")]
    )
    # Append it to state
    return {"analysis": analysis_results.content}


def get_rejected_data(state: AnalysisState):
    """ Extracts the rejected data from the analysis results """
    analysis = state["analysis"]
    if "No validation errors detected" in analysis:
        return {"rejected_data": []}
    
    rejected_data_output = OPENAILLM.invoke(
        [SystemMessage(content="Please provide the specific data points that violate the rules in .json string format.")] +
        [HumanMessage(content=f"Analysis: {state["analysis"]}")] + 
        [HumanMessage(content=f"Source data: {state["clean_data"]}")]
    )
    return {"rejected_data": [rejected_data_output.content]}



def build_interview_graph():
    # Add nodes and edges 
    interview_builder = StateGraph(AnalysisState)
    interview_builder.add_node("analyse_data", analyse_data)
    interview_builder.add_node("get_rejected_data", get_rejected_data)
    # Flow
    interview_builder.add_edge(START, "analyse_data")
    interview_builder.add_edge("analyse_data", "get_rejected_data")
    interview_builder.add_edge("get_rejected_data", END)
    return interview_builder

