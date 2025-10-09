from typing import Dict, List, Optional

from pydantic import BaseModel


class SnowglobeData(BaseModel):
    conversation_id: str
    test_id: str


class SnowglobeMessage(BaseModel):
    role: str
    content: str
    snowglobe_data: Optional[SnowglobeData] = None


class CompletionFunctionOutputs(BaseModel):
    response: str


class CompletionRequest(BaseModel):
    messages: List[SnowglobeMessage]

    def to_openai_messages(self, system_prompt: Optional[str] = None) -> List[Dict]:
        """Return a list of OpenAI messages from the Snowglobe messages"""
        oai_messages = []

        if system_prompt:
            oai_messages.append({"role": "system", "content": system_prompt})

        oai_messages.extend(
            [{"role": msg.role, "content": msg.content} for msg in self.messages]
        )
        return oai_messages

    def get_prompt(self) -> str:
        """Return the prompt from the Snowglobe messages"""
        return self.to_openai_messages(system_prompt=None)[-1]["content"]

    def get_conversation_id(self) -> str:
        """Return the conversation id from the Snowglobe messages"""
        return self.messages[0].snowglobe_data.conversation_id


class RiskEvaluationRequest(BaseModel):
    messages: List[SnowglobeMessage]


class RiskEvaluationOutputs(BaseModel):
    triggered: bool
    tags: Optional[Dict[str, str]] = None
    reason: Optional[str] = None
    severity: Optional[int] = None
