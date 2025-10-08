from __future__ import annotations
from enum import StrEnum
from pydantic import BaseModel

class InvokationType(StrEnum):
    INCOMING_MESSAGE = "incoming_message"
    FOLLOW_UP = "follow_up"
    SINGLE_QUALITY_TEST = "single_quality_test"
    ALL_QUALITY_TEST = "all_quality_test"
    SMART_TAGGING = "smart_tagging"
    QUALITY_TEST_INTERACTION = "quality_test_interaction"
    # Callback-specific types
    INCOMING_MESSAGE_CALLBACK = "incoming_message_callback"
    SINGLE_QUALITY_TEST_CALLBACK = "single_quality_test_callback"
    SMART_TAGGING_CALLBACK = "smart_tagging_callback"


class LambdaAiEvent(BaseModel):
    type: InvokationType
    data: dict
