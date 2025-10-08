from pydantic import BaseModel, Field
from typing import Dict, Any

from letschatty.models.utils.types.identifier import StrObjectId
from .lambda_invokation_types import InvokationType, LambdaAiEvent
from .expected_output import ExpectedOutputIncomingMessage, ExpectedOutputSmartTag, ExpectedOutputQualityTest, IncomingMessageAIDecision
from ...models.company.assets.ai_agents_v2.ai_agents_decision_output import IncomingMessageDecisionAction

class SmartTaggingCallbackMetadata(BaseModel):
    chat_id: StrObjectId
    company_id: StrObjectId

class ComparisonAnalysisCallbackMetadata(BaseModel):
    test_case_id: StrObjectId
    company_id : StrObjectId

class InteractionCallbackMetadata(BaseModel):
    test_case_id: StrObjectId
    chat_example_id: StrObjectId
    ai_agent_id: StrObjectId
    company_id: StrObjectId
    interaction_index: int

class IncomingMessageCallbackEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.INCOMING_MESSAGE_CALLBACK
    data: IncomingMessageAIDecision
    callback_metadata: Dict[str, Any] = Field(default_factory=dict)

class QualityTestCallbackEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.SINGLE_QUALITY_TEST_CALLBACK
    data: ExpectedOutputQualityTest
    callback_metadata: ComparisonAnalysisCallbackMetadata

class QualityTestInteractionCallbackEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.QUALITY_TEST_INTERACTION
    data: ExpectedOutputIncomingMessage
    callback_metadata: InteractionCallbackMetadata

class SmartTaggingCallbackEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.SMART_TAGGING_CALLBACK
    data: ExpectedOutputSmartTag
    callback_metadata: SmartTaggingCallbackMetadata

class ChatData(BaseModel):
    chat_id: StrObjectId
    company_id: StrObjectId

class IncomingMessageEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.INCOMING_MESSAGE
    data: ChatData

class FollowUpEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.FOLLOW_UP
    data: ChatData

class QualityTestEventData(BaseModel):
    chat_example_id: StrObjectId
    company_id: StrObjectId
    ai_agent_id: StrObjectId

class QualityTestEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.SINGLE_QUALITY_TEST
    data: QualityTestEventData

class AllQualityTestEventData(BaseModel):
    company_id: StrObjectId
    ai_agent_id: StrObjectId

class AllQualityTestEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.ALL_QUALITY_TEST
    data: AllQualityTestEventData

class SmartTaggingEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.SMART_TAGGING
    data: ChatData
