from importlib import import_module, metadata
import os
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable, Collection, Dict, TypedDict, Union
from functools import wraps

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from snowglobe.client.src.models import (
    CompletionRequest,
    CompletionFunctionOutputs,
    RiskEvaluationRequest,
    RiskEvaluationOutputs,
)
from snowglobe.client.src.types import (
    CompletionFnTelemetryContext,
    RiskEvalTelemetryContext,
)

import mlflow
import mlflow.tracing
from mlflow.client import MlflowClient
from mlflow.entities import Experiment, Run, ViewType
from databricks.sdk import WorkspaceClient
from databricks.sdk.errors.platform import NotFound

mlflow.tracing.enable()


class RunCacheEntry(TypedDict):
    run: Run
    expires_at: datetime


class ExperimentCacheEntry(TypedDict):
    experiment: Experiment
    expires_at: datetime


class MLflowInstrumentor(BaseInstrumentor):
    _snowglobe_version: str
    _run_completion_fn: Callable[
        [
            Union[
                Callable[[CompletionRequest], CompletionFunctionOutputs],
                Callable[[CompletionRequest], Awaitable[CompletionFunctionOutputs]],
            ],
            CompletionRequest,
            CompletionFnTelemetryContext,
        ],
        Awaitable[CompletionFunctionOutputs],
    ]
    _run_risk_evaluation_fn: Callable[
        [
            Union[
                Callable[[RiskEvaluationRequest], RiskEvaluationOutputs],
                Callable[[RiskEvaluationRequest], Awaitable[RiskEvaluationOutputs]],
            ],
            RiskEvaluationRequest,
            RiskEvalTelemetryContext,
        ],
        Awaitable[RiskEvaluationOutputs],
    ]

    _run_cache: Dict[str, RunCacheEntry]
    _experiment_cache: Dict[str, ExperimentCacheEntry]

    def __init__(self):
        super().__init__()
        self._snowglobe_version = metadata.version("snowglobe")
        runner = import_module("snowglobe.client.src.runner")
        self._run_completion_fn = runner.run_completion_fn
        self._run_risk_evaluation_fn = runner.run_risk_evaluation_fn
        self.mlflow_client = MlflowClient()
        self._run_cache = {}
        self._experiment_cache = {}

    def _get_default_experiment_name_prefix(self) -> str:
        MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
        prefix = ""
        current_user = None
        if MLFLOW_TRACKING_URI == "databricks":
            # DON'T try/catch this bc it's required if sending to a hosted tracking server in databricks
            w = WorkspaceClient()
            current_user = w.current_user.me()
        else:
            # DO try/catch this bc the user may or may not be using databricks; could be local or self-hosted
            try:
                w = WorkspaceClient()
                current_user = w.current_user.me()
            except Exception:
                pass

        if current_user:
            prefix = f"/Users/{current_user.user_name}/"

        return prefix

    def _cleanup_experiment_cache(self):
        now = datetime.now()

        expired_entries = []
        for key, entry in self._experiment_cache.items():
            if entry["expires_at"] < now:
                expired_entries.append(key)

        # Bc mutating a dictionary's length while iterating can cause issues
        for key in expired_entries:
            del self._experiment_cache[key]

    def _cleanup_run_cache(self):
        now = datetime.now()

        expired_entries = []
        for key, entry in self._run_cache.items():
            if entry["expires_at"] < now:
                expired_entries.append(key)

        # Bc mutating a dictionary's length while iterating can cause issues
        for key in expired_entries:
            run_entry = self._run_cache[key]
            run = run_entry["run"]
            # TODO: We need a better way to end the Run when a simulation ends,
            #   probably requires additional polling though.
            self.mlflow_client.update_run(run.info.run_id, status="FINISHED")
            del self._run_cache[key]

    def _get_or_create_experiment(self, experiment_name: str) -> Experiment:
        experiment = None
        one_hour = timedelta(hours=1)
        experiment_cache_entry = self._experiment_cache.get(experiment_name, None)

        if experiment_cache_entry:
            experiment = experiment_cache_entry["experiment"]
            exp_cache_entry_expiration = experiment_cache_entry["expires_at"]
            experiment_cache_entry["expires_at"] = exp_cache_entry_expiration + one_hour
            self._cleanup_experiment_cache()
            return experiment

        try:
            experiment = self.mlflow_client.get_experiment_by_name(experiment_name)
        except NotFound:
            experiment = None

        if not experiment:
            experiment_id = self.mlflow_client.create_experiment(experiment_name)
            experiment = self.mlflow_client.get_experiment(experiment_id)

        now = datetime.now()
        self._experiment_cache[experiment_name] = {
            "experiment": experiment,
            "expires_at": now + one_hour,
        }

        self._cleanup_experiment_cache()

        return experiment

    def _get_or_create_run(self, experiment_id: str, simulation_name: str) -> Run:
        run = None
        fifteen_minutes = timedelta(minutes=15)
        cache_key = f"{experiment_id}/{simulation_name}"
        run_cache_entry = self._run_cache.get(cache_key, None)

        if run_cache_entry:
            run = run_cache_entry["run"]
            run_cache_entry_expiration = run_cache_entry["expires_at"]
            run_cache_entry["expires_at"] = run_cache_entry_expiration + fifteen_minutes
            self._run_cache[cache_key] = run_cache_entry
            self._cleanup_run_cache()
            return run

        try:
            search_runs_result = self.mlflow_client.search_runs(
                experiment_ids=[experiment_id],
                filter_string=f"run_name='{simulation_name}'",
                run_view_type=ViewType.ACTIVE_ONLY,
            )
            if search_runs_result:
                run = search_runs_result[0]
                now = datetime.now()
                self._run_cache[cache_key] = {
                    "run": run,
                    "expires_at": now + fifteen_minutes,
                }
                self._cleanup_run_cache()
                return run
        except NotFound:
            run = None

        if not run:
            run = self.mlflow_client.create_run(
                experiment_id=experiment_id, run_name=simulation_name
            )
            now = datetime.now()
            self._run_cache[cache_key] = {
                "run": run,
                "expires_at": now + fifteen_minutes,
            }

        self._cleanup_run_cache()

        return run

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["snowglobe >= 0.4.16"]

    def _instrument(self, **kwargs: Any):
        runner = import_module("snowglobe.client.src.runner")

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
        ] = runner.run_completion_fn
        wrapped_run_completion_fn = self._instrument_completion_fn(run_completion_fn)
        setattr(runner, "run_completion_fn", wrapped_run_completion_fn)
        setattr(runner.run_completion_fn, "__instrumented_by_mlflow", True)

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
        ] = runner.run_risk_evaluation_fn
        wrapped_risk_evaluation_fn = self._instrument_risk_evaluation_fn(
            run_risk_evaluation_fn
        )
        setattr(runner, "run_risk_evaluation_fn", wrapped_risk_evaluation_fn)
        setattr(runner.run_risk_evaluation_fn, "__instrumented_by_mlflow", True)

    def _uninstrument(self, **kwargs: Any):
        runner = import_module("snowglobe.client.src.runner")
        if self._run_completion_fn:
            setattr(runner, "run_completion_fn", self._run_completion_fn)
            delattr(runner.run_completion_fn, "__instrumented_by_mlflow")

        if self._run_risk_evaluation_fn:
            setattr(runner, "run_risk_evaluation_fn", self._run_risk_evaluation_fn)
            delattr(runner.run_risk_evaluation_fn, "__instrumented_by_mlflow")

    def _instrument_completion_fn(
        self,
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
    ):
        default_exp_name_prefix = self._get_default_experiment_name_prefix()

        @wraps(run_completion_fn)
        async def run_completion_fn_wrapper(
            completion_fn: Union[
                Callable[[CompletionRequest], CompletionFunctionOutputs],
                Callable[[CompletionRequest], Awaitable[CompletionFunctionOutputs]],
            ],
            completion_request: CompletionRequest,
            telemetry_context: CompletionFnTelemetryContext,
        ) -> CompletionFunctionOutputs:
            try:
                session_id = telemetry_context["session_id"]
                conversation_id = telemetry_context["conversation_id"]
                message_id = telemetry_context["message_id"]
                simulation_name = telemetry_context["simulation_name"]
                agent_name = telemetry_context["agent_name"]
                span_type = telemetry_context["span_type"]

                formatted_agent_name = agent_name.lower().replace(" ", "_")
                default_experiment_name = (
                    f"{default_exp_name_prefix}{formatted_agent_name}"
                )

                mlflow_experiment_name = (
                    os.getenv("MLFLOW_EXPERIMENT_NAME") or default_experiment_name
                )
                mlflow.set_experiment(mlflow_experiment_name)

                mlflow_active_model_id = os.getenv("MLFLOW_ACTIVE_MODEL_ID")
                if mlflow_active_model_id:
                    mlflow.set_active_model(model_id=mlflow_active_model_id)

                experiment = self._get_or_create_experiment(mlflow_experiment_name)

                run = self._get_or_create_run(experiment.experiment_id, simulation_name)

                span_attributes = {
                    "snowglobe.version": self._snowglobe_version,
                    "session_id": str(session_id),
                    "snowglobe.span.type": span_type,
                    "snowglobe.session.id": str(session_id),
                    "snowglobe.conversation.id": str(conversation_id),
                    "snowglobe.message.id": str(message_id),
                    "snowglobe.simulation.name": simulation_name,
                    "snowglobe.agent.name": agent_name,
                }

                @mlflow.trace(
                    name=span_type,
                    span_type=span_type,
                    attributes=span_attributes,
                )
                @wraps(completion_fn)
                async def completion_fn_wrapper(
                    req: CompletionRequest,
                ) -> CompletionFunctionOutputs:
                    try:
                        mlflow.update_current_trace(
                            metadata={"mlflow.trace.session": str(session_id)},
                            tags={
                                "session_id": str(session_id),
                                "experiment_name": mlflow_experiment_name,
                                "snowglobe.session.id": str(session_id),
                                "snowglobe.conversation.id": str(conversation_id),
                                "snowglobe.message.id": str(message_id),
                                "snowglobe.simulation.name": simulation_name,
                                "snowglobe.agent.name": agent_name,
                            },
                        )
                        span = mlflow.get_current_active_span()
                        if span:
                            try:
                                self.mlflow_client.link_traces_to_run(
                                    trace_ids=[span.trace_id], run_id=run.info.run_id
                                )
                            except Exception:
                                pass
                        completion_fn_out = completion_fn(req)
                        if isinstance(completion_fn_out, Awaitable):
                            awaited_completion_fn_out = await completion_fn_out
                            return awaited_completion_fn_out
                        return completion_fn_out
                    except Exception as e:
                        raise e

                completion_fn_wrapper_out = await completion_fn_wrapper(
                    completion_request
                )
                return completion_fn_wrapper_out
            except Exception as e:
                raise e

        return run_completion_fn_wrapper

    def _instrument_risk_evaluation_fn(
        self,
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
    ):
        default_exp_name_prefix = self._get_default_experiment_name_prefix()

        @wraps(run_risk_evaluation_fn)
        async def run_risk_evaluation_fn_wrapper(
            risk_evaluation_fn: Union[
                Callable[[RiskEvaluationRequest], RiskEvaluationOutputs],
                Callable[[RiskEvaluationRequest], Awaitable[RiskEvaluationOutputs]],
            ],
            risk_evaluation_request: RiskEvaluationRequest,
            telemetry_context: RiskEvalTelemetryContext,
        ) -> RiskEvaluationOutputs:
            try:
                session_id = telemetry_context["session_id"]
                conversation_id = telemetry_context["conversation_id"]
                message_id = telemetry_context["message_id"]
                simulation_name = telemetry_context["simulation_name"]
                agent_name = telemetry_context["agent_name"]
                span_type = telemetry_context["span_type"]
                risk_name = telemetry_context["risk_name"]

                formatted_agent_name = agent_name.lower().replace(" ", "_")
                default_experiment_name = (
                    f"{default_exp_name_prefix}{formatted_agent_name}"
                )

                mlflow_experiment_name = (
                    os.getenv("MLFLOW_EXPERIMENT_NAME") or default_experiment_name
                )
                mlflow.set_experiment(mlflow_experiment_name)

                mlflow_active_model_id = os.getenv("MLFLOW_ACTIVE_MODEL_ID")
                if mlflow_active_model_id:
                    mlflow.set_active_model(model_id=mlflow_active_model_id)

                experiment = self._get_or_create_experiment(mlflow_experiment_name)

                run = self._get_or_create_run(experiment.experiment_id, simulation_name)

                span_attributes = {
                    "snowglobe.version": self._snowglobe_version,
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
                @wraps(risk_evaluation_fn)
                async def risk_evaluation_fn_wrapper(
                    req: RiskEvaluationRequest,
                ):
                    try:
                        mlflow.update_current_trace(
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
                        span = mlflow.get_current_active_span()
                        if span:
                            try:
                                self.mlflow_client.link_traces_to_run(
                                    trace_ids=[span.trace_id], run_id=run.info.run_id
                                )
                            except Exception:
                                pass
                        risk_evaluation_fn_out = risk_evaluation_fn(req)
                        if isinstance(risk_evaluation_fn_out, Awaitable):
                            awaited_risk_evaluation_fn_out = (
                                await risk_evaluation_fn_out
                            )
                            return awaited_risk_evaluation_fn_out
                        return risk_evaluation_fn_out
                    except Exception as e:
                        raise e

                risk_evaluation_fn_wrapper_out = await risk_evaluation_fn_wrapper(
                    risk_evaluation_request
                )
                return risk_evaluation_fn_wrapper_out
            except Exception as e:
                raise e

        return run_risk_evaluation_fn_wrapper
