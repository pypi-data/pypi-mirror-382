import asyncio
from typing import Awaitable, Callable, cast, Coroutine, Union
from .models import (
    CompletionFunctionOutputs,
    CompletionRequest,
    RiskEvaluationOutputs,
    RiskEvaluationRequest,
)
from .types import (
    CompletionFnTelemetryContext,
    RiskEvalTelemetryContext,
)


async def run_completion_fn(
    completion_fn: Union[
        Callable[[CompletionRequest], CompletionFunctionOutputs],
        Callable[[CompletionRequest], Awaitable[CompletionFunctionOutputs]],
    ],
    completion_request: CompletionRequest,
    telemetry_context: CompletionFnTelemetryContext,  # noqa
) -> CompletionFunctionOutputs:
    if asyncio.iscoroutinefunction(completion_fn):
        try:
            asyncio.get_running_loop()
            awaitable_completion_output = completion_fn(completion_request)
            completion_output = await awaitable_completion_output
        except RuntimeError:
            awaitable_completion_output: Coroutine[
                None, None, CompletionFunctionOutputs
            ] = completion_fn(completion_request)
            completion_output = asyncio.run(awaitable_completion_output)
    else:
        sync_completion_fn = cast(
            Callable[[CompletionRequest], CompletionFunctionOutputs], completion_fn
        )
        completion_output = sync_completion_fn(completion_request)
    return completion_output


async def run_risk_evaluation_fn(
    risk_evaluation_fn: Union[
        Callable[[RiskEvaluationRequest], RiskEvaluationOutputs],
        Callable[[RiskEvaluationRequest], Awaitable[RiskEvaluationOutputs]],
    ],
    risk_evaluation_request: RiskEvaluationRequest,
    telemetry_context: RiskEvalTelemetryContext,  # noqa
) -> RiskEvaluationOutputs:
    if asyncio.iscoroutinefunction(risk_evaluation_fn):
        try:
            asyncio.get_running_loop()
            awaitable_risk_eval = risk_evaluation_fn(risk_evaluation_request)
            risk_evaluation = await awaitable_risk_eval
        except RuntimeError:
            awaitable_risk_eval: Coroutine[None, None, RiskEvaluationOutputs] = (
                risk_evaluation_fn(risk_evaluation_request)
            )
            risk_evaluation = asyncio.run(awaitable_risk_eval)
    else:
        # pyright doesn't understand that the above check means the function is synchronous here...
        sync_risk_evaluation_fn = cast(
            Callable[[RiskEvaluationRequest], RiskEvaluationOutputs], risk_evaluation_fn
        )
        risk_evaluation = sync_risk_evaluation_fn(risk_evaluation_request)
    return risk_evaluation
