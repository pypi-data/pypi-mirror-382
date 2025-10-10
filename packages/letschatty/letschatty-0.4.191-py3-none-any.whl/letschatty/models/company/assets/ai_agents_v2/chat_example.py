from pydantic import BaseModel, Field
from typing import List, Any, ClassVar
from enum import StrEnum
from letschatty.models.base_models.ai_agent_component import AiAgentComponent


class ExampleElementType(StrEnum):
    """Type of an example element"""
    USER = "user"
    AI = "ai"
    CHAIN_OF_THOUGHT = "chain_of_thought"

class ExampleElement(BaseModel):
    """An element of a chat example"""
    type: ExampleElementType = Field(..., description="Type of the element")
    content: str = Field(..., description="Content of the element")

    def to_string(self) -> str:
        return self.type.value + ": " + self.content

class ChatExample(AiAgentComponent):
    """Example conversation for training the AI agent"""
    content: List[ExampleElement] = Field(..., description="Sequence of elements in this example")
    is_essential: bool = Field(default=False, description="Whether the example is essential for the ai agent to work")
    is_training_example: bool = Field(default=True, description="Whether the example is a training example or just a test example")

    def to_string(self) -> str:
        result = ""
        for element in self.content:
            result += element.to_string() + "\n"
        return result