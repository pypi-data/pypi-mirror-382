from typing import TypedDict


class CompletionFnTelemetryContext(TypedDict):
    session_id: str
    conversation_id: str
    message_id: str
    simulation_name: str
    agent_name: str
    span_type: str


class RiskEvalTelemetryContext(TypedDict):
    session_id: str
    conversation_id: str
    message_id: str
    simulation_name: str
    agent_name: str
    span_type: str
    risk_name: str
