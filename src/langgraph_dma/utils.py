from typing import List, Optional, Annotated
from typing_extensions import TypedDict


# The structure of the logs
class RealTimeDataLogs(TypedDict):
    id: str
    raw_data: Optional[List]


