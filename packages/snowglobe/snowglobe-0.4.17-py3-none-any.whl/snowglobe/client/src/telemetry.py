import os
from importlib.metadata import version as importlib_version
from typing import Awaitable, Callable, Union
from functools import wraps

from .models import (
    CompletionRequest,
    CompletionFunctionOutputs,
    RiskEvaluationRequest,
    RiskEvaluationOutputs,
)
from .types import CompletionFnTelemetryContext, RiskEvalTelemetryContext

try:
    import mlflow  # type: ignore
    import mlflow.tracing  # type: ignore
    from databricks.sdk import WorkspaceClient

    mlflow.tracing.enable()
except ImportError:
    mlflow = None
    WorkspaceClient = None

SNOWGLOBE_VERSION = importlib_version("snowglobe")


def trace_completion_fn(
    *,
    session_id: str,
    conversation_id: str,
    message_id: str,
    simulation_name: str,
    agent_name: str,
    span_type: str,
):
    def trace_decorator(
        run_completion_fn: Callable[
            [
                Union[
                    Callable[[CompletionRequest], CompletionFunctionOutputs],
                    Callable[[CompletionRequest], Awaitable[CompletionFunctionOutputs]],
                ],
                CompletionRequest,
                CompletionFnTelemetryContext,
            ],
            Awaitable[CompletionFunctionOutputs],
        ],
    ) -> Callable[
        [
            Union[
                Callable[[CompletionRequest], CompletionFunctionOutputs],
                Callable[[CompletionRequest], Awaitable[CompletionFunctionOutputs]],
            ],
            CompletionRequest,
            CompletionFnTelemetryContext,
        ],
        Awaitable[CompletionFunctionOutputs],
    ]:
        disable_mlflow = os.getenv("SNOWGLOBE_DISABLE_MLFLOW_TRACING") or ""
        if mlflow is not None and disable_mlflow.lower() != "true":
            if not WorkspaceClient:
                raise RuntimeError(
                    "The databricks-sdk package must be installed for MLflow instrumentation!"
                )

            w = WorkspaceClient()
            current_user = w.current_user.me()

            formatted_sim_name = simulation_name.lower().replace(" ", "_")
            default_experiment_name = (
                f"/Users/{current_user.user_name}/{formatted_sim_name}"
            )

            mlflow_experiment_name = (
                os.getenv("MLFLOW_EXPERIMENT_NAME") or default_experiment_name
            )
            mlflow.set_experiment(mlflow_experiment_name)

            mlflow_active_model_id = os.getenv("MLFLOW_ACTIVE_MODEL_ID")
            if mlflow_active_model_id:
                mlflow.set_active_model(model_id=mlflow_active_model_id)
            else:
                mlflow.set_active_model(name=agent_name)

            span_attributes = {
                "snowglobe.version": SNOWGLOBE_VERSION,
                "type": span_type,
                "session_id": str(session_id),
                "conversation_id": str(conversation_id),
                "message_id": str(message_id),
                "simulation_name": simulation_name,
                "agent_name": agent_name,
            }

            @mlflow.trace(
                name=span_type,
                span_type=span_type,
                attributes=span_attributes,
            )
            @wraps(run_completion_fn)
            async def run_completion_fn_wrapper(
                completion_fn: Union[
                    Callable[[CompletionRequest], CompletionFunctionOutputs],
                    Callable[[CompletionRequest], Awaitable[CompletionFunctionOutputs]],
                ],
                completion_request: CompletionRequest,
                telemetry_context: CompletionFnTelemetryContext,
            ):
                try:
                    mlflow.update_current_trace(  # type: ignore
                        metadata={"mlflow.trace.session": str(session_id)},
                        tags={
                            "session_id": str(session_id),
                            "conversation_id": str(conversation_id),
                            "message_id": str(message_id),
                            "simulation_name": simulation_name,
                            "agent_name": agent_name,
                        },
                    )
                    response = await run_completion_fn(
                        completion_fn, completion_request, telemetry_context
                    )
                    return response
                except Exception as e:
                    raise e

            return run_completion_fn_wrapper
        else:
            return run_completion_fn

    return trace_decorator


def trace_risk_evaluation_fn(
    *,
    session_id: str,
    conversation_id: str,
    message_id: str,
    simulation_name: str,
    agent_name: str,
    span_type: str,
    risk_name,
):
    def trace_decorator(
        run_risk_evaluation_fn: Callable[
            [
                Union[
                    Callable[[RiskEvaluationRequest], RiskEvaluationOutputs],
                    Callable[[RiskEvaluationRequest], Awaitable[RiskEvaluationOutputs]],
                ],
                RiskEvaluationRequest,
                RiskEvalTelemetryContext,
            ],
            Awaitable[RiskEvaluationOutputs],
        ],
    ) -> Callable[
        [
            Union[
                Callable[[RiskEvaluationRequest], RiskEvaluationOutputs],
                Callable[[RiskEvaluationRequest], Awaitable[RiskEvaluationOutputs]],
            ],
            RiskEvaluationRequest,
            RiskEvalTelemetryContext,
        ],
        Awaitable[RiskEvaluationOutputs],
    ]:
        disable_mlflow = os.getenv("SNOWGLOBE_DISABLE_MLFLOW_TRACING") or ""
        if mlflow and disable_mlflow.lower() != "true":
            if not WorkspaceClient:
                raise RuntimeError(
                    "The databricks-sdk package must be installed for MLflow instrumentation!"
                )

            w = WorkspaceClient()
            current_user = w.current_user.me()

            formatted_sim_name = simulation_name.lower().replace(" ", "_")
            default_experiment_name = (
                f"/Users/{current_user.user_name}/{formatted_sim_name}"
            )

            mlflow_experiment_name = (
                os.getenv("MLFLOW_EXPERIMENT_NAME") or default_experiment_name
            )
            mlflow.set_experiment(mlflow_experiment_name)

            mlflow_active_model_id = os.getenv("MLFLOW_ACTIVE_MODEL_ID")
            if mlflow_active_model_id:
                mlflow.set_active_model(model_id=mlflow_active_model_id)
            else:
                mlflow.set_active_model(name=agent_name)

            span_attributes = {
                "snowglobe.version": SNOWGLOBE_VERSION,
                "type": span_type,
                "session_id": str(session_id),
                "conversation_id": str(conversation_id),
                "message_id": str(message_id),
                "simulation_name": simulation_name,
                "agent_name": agent_name,
                "risk_name": risk_name,
            }

            @mlflow.trace(
                name=span_type,
                span_type=span_type,
                attributes=span_attributes,
            )
            @wraps(run_risk_evaluation_fn)
            async def risk_evaluation_fn_wrapper(
                risk_evaluation_fn: Union[
                    Callable[[RiskEvaluationRequest], RiskEvaluationOutputs],
                    Callable[[RiskEvaluationRequest], Awaitable[RiskEvaluationOutputs]],
                ],
                risk_evaluation_request: RiskEvaluationRequest,
                telemetry_context: RiskEvalTelemetryContext,
            ):
                try:
                    mlflow.update_current_trace(  # type: ignore
                        metadata={"mlflow.trace.session": str(session_id)},
                        tags={
                            "session_id": str(session_id),
                            "conversation_id": str(conversation_id),
                            "message_id": str(message_id),
                            "simulation_name": simulation_name,
                            "agent_name": agent_name,
                            "risk_name": risk_name,
                        },
                    )
                    response = await run_risk_evaluation_fn(
                        risk_evaluation_fn, risk_evaluation_request, telemetry_context
                    )
                    return response
                except Exception as e:
                    raise e

            return risk_evaluation_fn_wrapper
        else:
            return run_risk_evaluation_fn

    return trace_decorator
