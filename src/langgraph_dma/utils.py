from typing import List, Optional, Annotated
from typing_extensions import TypedDict
# from pydantic import BaseModel, Field
# from IPython.display import Image, display
# from langgraph.graph import START, END, StateGraph
# from langgraph.checkpoint.memory import MemorySaver
# from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


# The structure of the logs
class RealTimeDataLogs(TypedDict):
    id: str
    raw_data: Optional[List]