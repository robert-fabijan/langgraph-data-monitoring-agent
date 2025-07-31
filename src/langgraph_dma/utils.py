from typing import List, Optional, Annotated
from typing_extensions import TypedDict
# from pydantic import BaseModel, Field
# from IPython.display import Image, display
# from langgraph.graph import START, END, StateGraph
# from langgraph.checkpoint.memory import MemorySaver
# from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import datetime
import random as rand

# The structure of the logs
class RealTimeDataLogs(TypedDict):
    id: str
    raw_data: Optional[List]



def tool_read_etl_job_status(id: str):
    """
    Simulate reading the job status from a database or external service.
    This is a placeholder function that should be replaced with actual logic.
    Randomly sets status and error accordingly.
    """
    status = rand.choice(["running", "failed", "completed"])
    error = None
    if status == "failed":
        error = "ETL job failed due to timeout error."
    return {
        "id": id,
        "status": status,
        "error": error,
        "timestamp": datetime.datetime.now().isoformat(),
    }


def tool_read_connector_status(id: str):
    """
    Simulate reading the connector status from a database or external service.
    This is a placeholder function that should be replaced with actual logic.
    Randomly sets status and error accordingly.
    """
    status = rand.choice(["active", "inactive", "error"])
    error = None
    if status == "inactive":
        error = "Connector is inactive."
    elif status == "error":
        error = "Connector encountered an error."
    return {
        "id": id,
        "status": status,
        "error": error,
        "timestamp": datetime.datetime.now().isoformat(),
    }


def tool_read_api(source: str):
    """
    Simulate reading data from an API.
    This is a placeholder function that should be replaced with actual logic.
    Randomly returns data or an empty list. If empty, returns an error.
    """
    # Randomly decide to return data or an empty list
    if rand.choice([True, False]):
        data = [
            {"id": "1", "value": "data1"},
            {"id": "2", "value": "data2"},
        ]
        error = None
    else:
        data = []
        error = "No data available from API."

    return {
        "source": source,
        "data": data,
        "error": error,
        "timestamp": datetime.datetime.now().isoformat(),
    }