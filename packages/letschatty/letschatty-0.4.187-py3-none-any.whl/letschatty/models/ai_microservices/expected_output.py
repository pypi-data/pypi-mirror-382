from letschatty.models.company.assets.ai_agents_v2.chain_of_thought_in_chat import ChainOfThoughtInChatTrigger
from letschatty.models.messages.chatty_messages.base.message_draft import MessageDraft
from letschatty.models.messages.chatty_messages.schema.chatty_content.content_text import ChattyContentText
from letschatty.models.utils.types import StrObjectId
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal
from datetime import datetime

from letschatty.models.utils.types.message_types import MessageType
from ...models.company.assets.ai_agents_v2.ai_agents_decision_output import ChainOfThoughtInChatRequest, IncomingMessageAIDecision, IncomingMessageDecisionAction
from ...models.company.assets.automation import Automation

class ExpectedOutputQualityTest(BaseModel):
    accuracy: float = Field(description="The accuracy of the comparison analysis")
    comments: Optional[str] = Field(description="The comments of the comparison analysis")

class ExpectedOutputSmartTag(BaseModel):
    automation : Automation
    chain_of_thought: ChainOfThoughtInChatRequest = Field(description="REQUIRED: Your reasoning process and response decision explanation")

class ExpectedOutputIncomingMessage(BaseModel):
    action: IncomingMessageDecisionAction
    messages: List[str] = Field(description="Array of message strings to send to the customer. Required for send/suggest actions, optional for escalate action, empty array for skip/remove actions.")
    chain_of_thought: ChainOfThoughtInChatRequest = Field(description="REQUIRED: Your reasoning process and response decision explanation")

    def to_incoming_message_decision_output(self) -> IncomingMessageAIDecision:
        messages_drafts = [
            MessageDraft(
                type=MessageType.TEXT,
                content=ChattyContentText(body=message),
                is_incoming_message=False
            )
            for message in self.messages
        ]
        incoming_decision = IncomingMessageAIDecision(
            action=self.action,
            messages=messages_drafts,
            chain_of_thought=self.chain_of_thought
        )
        return incoming_decision


