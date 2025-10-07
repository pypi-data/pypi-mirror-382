# © Copyright Databand.ai, an IBM Company 2022

import datetime
import logging
import typing

import dbnd

from dbnd._core.constants import (
    DbndDatasetOperationType,
    DbndTargetOperationStatus,
    DbndTargetOperationType,
)
from dbnd._core.tracking.backends.abstract_tracking_store import TrackingStore
from dbnd._core.tracking.backends.channels.abstract_channel import TrackingChannel
from dbnd._core.tracking.schemas.metrics import Metric
from dbnd._core.tracking.tracking_info_convertor import TrackingInfoBuilder
from dbnd._core.utils import json_utils
from dbnd._core.utils.timezone import utcnow
from dbnd.api.tracking_api import (
    LogDatasetArgs,
    LogTargetArgs,
    TaskRunAttemptUpdateArgs,
    add_task_runs_schema,
    airflow_task_infos_schema,
    heartbeat_schema,
    init_run_schema,
    log_artifact_schema,
    log_datasets_schema,
    log_dbt_metadata_schema,
    log_metrics_schema,
    log_targets_schema,
    save_external_links_schema,
    save_task_run_log_schema,
    scheduled_job_args_schema,
    set_run_state_schema,
    set_task_run_reused_schema,
    set_unfinished_tasks_state_schema,
    update_task_run_attempts_schema,
)
from targets import Target
from targets.value_meta import ValueMeta


if typing.TYPE_CHECKING:
    from typing import Any, Iterable, List, Optional, Union
    from uuid import UUID

    from dbnd._core.constants import TaskRunState
    from dbnd._core.task_run.task_run import TaskRun
    from dbnd._core.task_run.task_run_error import TaskRunError

logger = logging.getLogger(__name__)


class TrackingStoreThroughChannel(TrackingStore):
    """Track data to Tracking API"""

    def __init__(self, channel: TrackingChannel, *args, **kwargs):
        super(TrackingStoreThroughChannel, self).__init__(*args, **kwargs)
        self.channel = channel

    def init_scheduled_job(self, scheduled_job, update_existing):
        marsh = scheduled_job_args_schema.dump(
            dict(scheduled_job_args=scheduled_job, update_existing=update_existing)
        )
        resp = self.channel.init_scheduled_job(marsh.data)
        return resp

    def init_run(self, run):
        init_args = TrackingInfoBuilder(run).build_init_args()
        return self.init_run_from_args(init_args=init_args)

    def init_run_from_args(self, init_args):
        marsh = init_run_schema.dump(
            dict(init_args=init_args, version=dbnd.__version__)
        )
        resp = self.channel.init_run(marsh.data)
        return resp

    def add_task_runs(self, run, task_runs):
        task_runs_info = TrackingInfoBuilder(run).build_task_runs_info(
            task_runs=task_runs, dynamic_task_run_update=True
        )
        marsh = add_task_runs_schema.dump(
            dict(task_runs_info=task_runs_info, source=run.source)
        )
        resp = self.channel.add_task_runs(marsh.data)
        return resp

    def set_run_state(self, run, state, error=None, timestamp=None):
        marsh = set_run_state_schema.dump(
            dict(run_uid=run.run_uid, state=state, timestamp=timestamp)
        )
        resp = self.channel.set_run_state(marsh.data)
        return resp

    def set_task_reused(self, task_run):
        marsh = set_task_run_reused_schema.dump(
            dict(
                task_run_uid=task_run.task_run_uid,
                task_outputs_signature=task_run.task.task_outputs_signature_obj.signature,
            )
        )
        resp = self.channel.set_task_reused(marsh.data)
        return resp

    def set_task_run_state(self, task_run, state, error=None, timestamp=None):
        # type: (TaskRun, TaskRunState, TaskRunError, datetime.datetime) -> None
        marsh = update_task_run_attempts_schema.dump(
            dict(
                task_run_attempt_updates=[
                    TaskRunAttemptUpdateArgs(
                        task_run_uid=task_run.task_run_uid,
                        task_run_attempt_uid=task_run.task_run_attempt_uid,
                        state=state,
                        error=error.as_error_info() if error else None,
                        timestamp=timestamp or utcnow(),
                        source=task_run.run.source,
                    )
                ]
            )
        )
        resp = self.channel.update_task_run_attempts(marsh.data)
        return resp

    def set_task_run_states(self, task_runs):
        marsh = update_task_run_attempts_schema.dump(
            dict(
                task_run_attempt_updates=[
                    TaskRunAttemptUpdateArgs(
                        task_run_uid=task_run.task_run_uid,
                        task_run_attempt_uid=task_run.task_run_attempt_uid,
                        state=task_run.task_run_state,
                        timestamp=utcnow(),
                        source=task_run.run.source,
                    )
                    for task_run in task_runs
                ]
            )
        )
        resp = self.channel.update_task_run_attempts(marsh.data)
        return resp

    def set_unfinished_tasks_state(self, run_uid, state):
        marsh = set_unfinished_tasks_state_schema.dump(
            dict(run_uid=run_uid, state=state, timestamp=utcnow())
        )
        resp = self.channel.set_unfinished_tasks_state(marsh.data)
        return resp

    def update_task_run_attempts(self, task_run_attempt_updates):
        marsh = update_task_run_attempts_schema.dump(
            dict(task_run_attempt_updates=task_run_attempt_updates)
        )
        resp = self.channel.update_task_run_attempts(marsh.data)
        return resp

    def save_task_run_log(self, task_run, log_body, local_log_path=None):
        marsh = save_task_run_log_schema.dump(
            dict(
                task_run_attempt_uid=task_run.task_run_attempt_uid,
                log_body=log_body,
                local_log_path=local_log_path,
            )
        )
        resp = self.channel.save_task_run_log(marsh.data)
        return resp

    def save_external_links(self, task_run, external_links_dict):
        marsh = save_external_links_schema.dump(
            dict(
                task_run_attempt_uid=task_run.task_run_attempt_uid,
                external_links_dict=external_links_dict,
            )
        )
        resp = self.channel.save_external_links(marsh.data)
        return resp

    def log_dataset(
        self,
        task_run,  # type: TaskRun
        operation_path,  # type: Union[Target, str]
        data_meta,  # type: ValueMeta
        operation_type,  # type: DbndDatasetOperationType
        operation_status,  # type: DbndTargetOperationStatus
        operation_error,  # type: str
        operation_source=None,  # type: Optional[str]
        with_partition=None,  # type: Optional[bool]
    ):
        dataset_info = LogDatasetArgs(
            run_uid=task_run.run.run_uid,
            task_run_uid=task_run.task_run_uid,
            task_run_name=task_run.task_af_id,
            task_run_attempt_uid=task_run.task_run_attempt_uid,
            operation_path=str(operation_path),
            operation_type=operation_type,
            operation_status=operation_status,
            operation_error=operation_error,
            operation_source=operation_source,
            value_preview=data_meta.value_preview,
            columns_stats=data_meta.columns_stats,
            data_dimensions=data_meta.data_dimensions,
            data_schema=data_meta.data_schema,
            query=data_meta.query,
            with_partition=with_partition,
            timestamp=utcnow(),
            dataset_uri=None,
        )
        res = self.log_datasets(datasets_info=[dataset_info])
        return res

    def log_datasets(self, datasets_info):  # type: (List[LogDatasetArgs]) -> Any
        marsh = log_datasets_schema.dump(dict(datasets_info=datasets_info))
        resp = self.channel.log_datasets(marsh.data)
        return resp

    def log_dbt_metadata(self, dbt_run_metadata, task_run):
        marsh = log_dbt_metadata_schema.dump(
            dict(
                dbt_run_metadata=dbt_run_metadata,
                task_run_attempt_uid=task_run.task_run_attempt_uid,
            )
        )
        resp = self.channel.log_dbt_metadata(marsh.data)
        return resp

    def log_target(
        self,
        task_run,
        target,
        target_meta,  # type: ValueMeta
        operation_type,  # type: DbndTargetOperationType
        operation_status,  # type: DbndTargetOperationStatus
        param_name=None,  # type: Optional[str]
        task_def_uid=None,  # type: Optional[UUID]
    ):
        data_schema = (
            json_utils.dumps(target_meta.data_schema.as_dict())
            if target_meta.data_schema is not None
            else None
        )
        target_info = LogTargetArgs(
            run_uid=task_run.run.run_uid,
            task_run_uid=task_run.task_run_uid,
            task_run_name=task_run.job_name,
            task_run_attempt_uid=task_run.task_run_attempt_uid,
            task_def_uid=task_def_uid,
            param_name=param_name,
            target_path=str(target),
            operation_type=operation_type,
            operation_status=operation_status,
            value_preview=target_meta.value_preview,
            data_dimensions=target_meta.data_dimensions,
            data_schema=data_schema,
            data_hash=target_meta.data_hash,
        )
        res = self.log_targets(targets_info=[target_info])
        if target_meta.histograms:
            self.log_histograms(task_run, param_name, target_meta, utcnow())
        return res

    def log_targets(self, targets_info):  # type: (List[LogTargetArgs]) -> None
        marsh = log_targets_schema.dump(dict(targets_info=targets_info))
        resp = self.channel.log_targets(marsh.data)
        return resp

    def log_histograms(self, task_run, key, value_meta, timestamp):
        value_meta_metrics = value_meta._build_metrics_for_key(key)
        if value_meta_metrics["histograms"]:
            self.log_metrics(
                task_run=task_run, metrics=value_meta_metrics["histograms"]
            )

    def log_metrics(self, task_run, metrics):
        # type: (TaskRun, Iterable[Metric]) -> None
        metrics_info = [
            {
                "task_run_attempt_uid": task_run.task_run_attempt_uid,
                "metric": metric,
                "source": metric.source,
            }
            for metric in metrics
        ]
        marsh = log_metrics_schema.dump(dict(metrics_info=metrics_info))
        resp = self.channel.log_metrics(marsh.data)
        return resp

    def log_artifact(self, task_run, name, artifact, artifact_target):
        marsh = log_artifact_schema.dump(
            dict(
                task_run_attempt_uid=task_run.task_run_attempt_uid,
                name=name,
                path=artifact_target.path,
            )
        )
        resp = self.channel.log_artifact(marsh.data)
        return resp

    def heartbeat(self, run_uid):
        marsh = heartbeat_schema.dump(dict(run_uid=run_uid))
        resp = self.channel.heartbeat(marsh.data)
        return resp

    def save_airflow_task_infos(self, airflow_task_infos, source, base_url):
        marsh = airflow_task_infos_schema.dump(
            dict(
                airflow_task_infos=airflow_task_infos, source=source, base_url=base_url
            )
        )
        resp = self.channel.save_airflow_task_infos(marsh.data)
        return resp

    def flush(self):
        self.channel.flush()

    def is_ready(self):
        return self.channel.is_ready()

    def __str__(self):
        return "TrackingStoreThroughChannel with channel=%s" % (str(self.channel),)

    @staticmethod
    def build_with_disabled_channel(databand_ctx):
        from dbnd._core.tracking.backends.channels.tracking_disabled_channel import (
            DisabledTrackingChannel,
        )

        return TrackingStoreThroughChannel(channel=DisabledTrackingChannel())

    @staticmethod
    def build_with_console_debug_channel(databand_ctx):
        from dbnd._core.tracking.backends.channels.tracking_debug_channel import (
            ConsoleDebugTrackingChannel,
        )

        return TrackingStoreThroughChannel(channel=ConsoleDebugTrackingChannel())

    @staticmethod
    def build_with_web_channel(databand_ctx):
        from dbnd._core.tracking.backends.channels.tracking_web_channel import (
            TrackingWebChannel,
        )

        return TrackingStoreThroughChannel(
            channel=TrackingWebChannel(
                databand_api_client=databand_ctx.databand_api_client
            )
        )

    @staticmethod
    def build_with_async_web_channel(databand_ctx):
        from dbnd._core.tracking.backends.channels.tracking_async_web_channel import (
            TrackingAsyncWebChannel,
        )

        parameters = {
            "max_retries": databand_ctx.settings.core.max_tracking_store_retries,
            "remove_failed_store": databand_ctx.settings.core.remove_failed_store,
            "tracker_raise_on_error": databand_ctx.settings.core.tracker_raise_on_error,
            "is_verbose": databand_ctx.system_settings.verbose,
            "databand_api_client": databand_ctx.databand_api_client,
        }

        return TrackingStoreThroughChannel(
            channel=TrackingAsyncWebChannel(**parameters)
        )
