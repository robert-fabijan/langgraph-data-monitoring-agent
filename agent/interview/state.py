from langgraph.graph import START, END, StateGraph,MessagesState
from langchain_core.messages import  SystemMessage, HumanMessage
from operator import add
from typing import List, Optional, Annotated
from langgraph_dma.personas import ITSupport
from langgraph_dma.llm import OPENAILLM
import logging

persona = ITSupport(
    affiliation="Tech Support",
    name="Alex",
    role="IT Support Analyst",
    description="""
        Responsible for monitoring and analyzing data quality for a specific system or asset.
        Focuses on assessing the health and reliability of data, identifying issues.
        Providing actionable insights from an IT support perspective.
    """
)

class InterviewState(MessagesState):
    max_num_turns: int # Number turns of conversation
    context: Annotated[list, add] # Source docs
    # analyst: ITSupport # Analyst asking questions
    clean_data: List[str] # Cleaned data logs
    # interview: str # Interview transcript
    summary: list # Final key we duplicate in outer state for Send() API


section_writer_instructions = """
You are an expert IT Support analyst.

Your task is to create a short, easily digestible section of a report based on the current state and condition of monitored data.

1. Analyze the data provided:
- Review metrics such as null values, threshold breaches, anomalies, and overall data health.

2. Create a report structure using markdown formatting:
- Use ## for the section title
- Use ### for sub-section headers

3. Write the report following this structure:
a. Title (## header)
b. Summary (### header)
c. Data Review (### header)
d. Recommendations (### header)

4. Focus on following tasks: {focus}

5. For the summary section:
- Provide general background/context related to the focus area
- Emphasize what is novel, interesting, or surprising about the data's current state
- Create a numbered list of key findings as you review the data
- Do not mention the names of interviewers or experts
- Aim for approximately 400 words maximum

6. In the Data Review section:
- Include all relevant metrics and observations
- Clearly state if data is in good condition, if thresholds are exceeded, or if there are too many nulls
- Separate each finding by a newline. Use two spaces at the end of each line to create a newline in Markdown.
- Example:

### Data Review
[1] Null values detected in POWER tag  
[2] Threshold exceeded for WIND_SPEED  

7. In the Recommendations section:
- Suggest actions to resolve or mitigate detected issues
- Provide clear, actionable steps for IT Support or stakeholders

8. Final review:
- Ensure the report follows the required structure
- Include no preamble before the title of the report
- Check that all guidelines have been followed
"""

def write_analysis(state: InterviewState):

    """ Node to answer a question """

    # Get state
    # interview = state["interview"]

    context = state["clean_data"]
    print()
    print("Context of subgraph")
    print(context)
    # analyst = state["analyst"]
   
    # Write section using either the gathered source docs from interview (context) or the interview itself (interview)
    system_message = section_writer_instructions.format(focus=persona.description)
    summary = OPENAILLM.invoke([SystemMessage(content=system_message)]+[HumanMessage(content=f"Use this source to write your section: {context}")]) 
    
    logging.info(f"Summary: {summary.content}")
    # Append it to state
    return {"summary": [summary.content]}

def build_interview_state():
    # Add nodes and edges 
    interview_builder = StateGraph(InterviewState)
    interview_builder.add_node("write_analysis", write_analysis)
    # Flow
    interview_builder.add_edge(START, "write_analysis")
    interview_builder.add_edge("write_analysis", END)
    return interview_builder

