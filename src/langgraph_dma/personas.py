# from typing import List, Optional, Annotated
# from typing_extensions import TypedDict
from pydantic import BaseModel, Field

class ITSupport(BaseModel):
    affiliation: str = Field(
        description="Primary affiliation of the ITSupport.",
    )
    name: str = Field(
        description="Name of the ITSupport."
    )
    role: str = Field(
        description="Role of the ITSupport in the context of the topic.",
    )
    description: str = Field(
        description="Description of the ITSupport focus, concerns, and motives.",
    )
    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nAffiliation: {self.affiliation}\nDescription: {self.description}\n"