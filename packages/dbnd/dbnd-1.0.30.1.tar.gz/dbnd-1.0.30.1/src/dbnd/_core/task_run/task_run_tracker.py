# © Copyright Databand.ai, an IBM Company 2022

import logging
import typing

from typing import Any, Dict, List, Optional, Union

import attr
import six

from dbnd._core.constants import (
    DbndDatasetOperationType,
    DbndTargetOperationStatus,
    DbndTargetOperationType,
    MetricSource,
)
from dbnd._core.errors.errors_utils import log_exception
from dbnd._core.log import dbnd_log_exception
from dbnd._core.log.external_exception_logging import capture_tracking_exception
from dbnd._core.parameter.parameter_definition import ParameterDefinition
from dbnd._core.settings.tracking_config import get_value_meta
from dbnd._core.task_run.task_run_ctrl import TaskRunCtrl
from dbnd._core.tracking.log_data_request import LogDataRequest
from dbnd._core.tracking.schemas.metrics import Metric
from dbnd._core.utils.timezone import utcnow
from targets import Target
from targets.value_meta import ValueMeta, ValueMetaConf


if typing.TYPE_CHECKING:
    from datetime import datetime

    import pandas as pd
    import pyspark.sql as spark

    from dbnd._core.tracking.backends import TrackingStore
    from dbnd_postgres.postgres_values import PostgresTable
    from dbnd_snowflake.snowflake_values import SnowflakeTable

logger = logging.getLogger(__name__)


class TaskRunTracker(TaskRunCtrl):
    def __init__(self, task_run, tracking_store):
        super(TaskRunTracker, self).__init__(task_run=task_run)
        self.tracking_store = tracking_store  # type: TrackingStore

    def task_run_url(self):
        run_tracker = self.run.tracker
        if not run_tracker.databand_url:
            return None

        return "{databand_url}/app/jobs/{job_name}/{run_uid}/{task_run_uid}".format(
            databand_url=run_tracker.databand_url,
            job_name=self.run.job_name,
            run_uid=self.run.run_uid,
            task_run_uid=self.task_run_uid,
        )

    # Task Handlers
    def save_task_run_log(self, log_preview, local_log_path=None):
        self.tracking_store.save_task_run_log(
            task_run=self.task_run, log_body=log_preview, local_log_path=local_log_path
        )

    def log_parameter_data(
        self, parameter, target, value, operation_type, operation_status
    ):
        # type: (TaskRunTracker, ParameterDefinition, Target, Any, DbndTargetOperationType, DbndTargetOperationStatus) -> None
        tracking_conf = self.settings.tracking
        if not tracking_conf.log_value_meta or value is None:
            return

        try:
            target.target_meta = get_value_meta(
                value,
                parameter.value_meta_conf,
                tracking_config=tracking_conf,
                value_type=parameter.value_type,
                target=target,
            )
            # FIXME If we failed to get target meta for some reason, target operation won't be logged!
            if target.target_meta is None:
                return

            self.tracking_store.log_target(
                task_run=self.task_run,
                target=target,
                target_meta=target.target_meta,
                operation_type=operation_type,
                operation_status=operation_status,
                param_name=parameter.name,
                task_def_uid=parameter.task_definition_uid,
            )
        except Exception as ex:
            log_exception(
                "Error occurred during target logging for %s" % (target,),
                ex,
                non_critical=True,
            )

    def _log_metrics(self, metrics):
        # type: (List[Metric]) -> None
        return self.tracking_store.log_metrics(task_run=self.task_run, metrics=metrics)

    def log_dbt_metadata(self, dbt_metadata):
        self.tracking_store.log_dbt_metadata(
            dbt_run_metadata=dbt_metadata, task_run=self.task_run
        )

    @capture_tracking_exception
    def log_metrics(self, metrics_dict, source=None, timestamp=None):
        # type: (Dict[str, Any], Optional[str], Optional[datetime]) -> None
        """
        Logs all the metrics in the metrics dict to the tracker.
        @param metrics_dict: name-value pairs of metrics to log
        @param source: optional name of the metrics source
        @param timestamp: optional timestamp of the metrics
        """
        metrics = [
            Metric(key=key, value=value, source=source, timestamp=timestamp or utcnow())
            for key, value in six.iteritems(metrics_dict)
        ]

        return self.tracking_store.log_metrics(task_run=self.task_run, metrics=metrics)

    def log_artifact(self, name, artifact):
        try:
            # file storage will save file
            # db will save path
            artifact_target = (
                self.task_run.task_run_executor.meta_files.get_artifact_target(name)
            )
            self.tracking_store.log_artifact(
                task_run=self.task_run,
                name=name,
                artifact=artifact,
                artifact_target=artifact_target,
            )
        except Exception as ex:
            log_exception(
                "Error occurred during log_artifact for %s" % (name,),
                ex,
                non_critical=True,
            )

    def log_metric(self, key, value, timestamp=None, source=None):
        # type: (str, Any, Optional[datetime], Optional[MetricSource]) -> None
        try:
            self.log_metrics({key: value}, source, timestamp)
        except Exception as ex:
            log_exception(
                "Error occurred during log_metric for %s" % (key,),
                ex,
                non_critical=True,
            )

    def log_data(
        self,
        key,  # type: str
        data,  # type: Union[pd.DataFrame, spark.DataFrame, PostgresTable, SnowflakeTable]
        meta_conf,  # type: ValueMetaConf
        path=None,  # type: Optional[Union[Target,str]]
        operation_type=DbndTargetOperationType.read,  # type: DbndTargetOperationType
        operation_status=DbndTargetOperationStatus.OK,  # type: DbndTargetOperationStatus
        raise_on_error=False,  # type: bool
    ):  # type: (...) -> None
        try:
            # Combine meta_conf with the config settings
            value_meta = get_value_meta(
                data, meta_conf, tracking_config=self.settings.tracking
            )
            if not value_meta:
                logger.warning(
                    "Couldn't log the wanted data {name}, reason - can't log objects of type {value_type} ".format(
                        name=key, value_type=type(data)
                    )
                )
                return

            ts = utcnow()

            if path:
                self.tracking_store.log_target(
                    task_run=self.task_run,
                    target=path,
                    target_meta=value_meta,
                    operation_type=operation_type,
                    operation_status=operation_status,
                    param_name=key,
                )

            self.log_value_metrics(key, meta_conf, value_meta, ts)

        except Exception as ex:
            log_exception(
                "Error occurred during log_dataframe for %s" % (key,),
                ex,
                non_critical=not raise_on_error,
            )
            if raise_on_error:
                raise

    def log_value_metrics(self, key, meta_conf, value_meta, ts=None):
        ts = ts or utcnow()
        metrics = value_meta._build_metrics_for_key(key, meta_conf)
        if metrics["user"]:
            self._log_metrics(metrics["user"])

        if metrics["histograms"]:
            self.tracking_store.log_histograms(
                task_run=self.task_run, key=key, value_meta=value_meta, timestamp=ts
            )
        if not (metrics["user"] or metrics["histograms"]):
            logger.info("No metrics to log_data(key={})".format(key))

    def log_dataset(self, op_report):
        # type: (DatasetOperationReport) -> None

        if op_report.meta_data:
            data_meta = op_report.meta_data
        else:
            data_meta = self._calc_meta_data(op_report.data, op_report.meta_conf)

        records, columns = data_meta.data_dimensions or (None, None)
        # if the row count or column count exist,
        # we need to override the match field(row/column) in data dimension
        # if one of them not exist we need to leave it with the original value
        # examples:
        # row_count=4, data_dimensions=(777,5) => data_dimensions=(4,5)
        # column_count=2, data_dimensions=(777,5) => data_dimensions=(777,2)
        if op_report.row_count or op_report.column_count:
            data_meta.data_dimensions = (
                op_report.row_count or records,
                op_report.column_count or columns,
            )
        self.tracking_store.log_dataset(
            task_run=self.task_run,
            operation_path=op_report.op_path,
            data_meta=data_meta,
            operation_type=op_report.op_type,
            operation_status=op_report.status,
            operation_error=op_report.error,
            operation_source=data_meta.op_source
            if data_meta.op_source
            else op_report.operation_source,
            with_partition=op_report.with_partition,
        )

        if op_report.send_metrics:
            dataset_name = _get_dataset_name(
                op_report.op_path, op_report.with_partition
            )

            self.log_value_metrics(dataset_name, op_report.meta_conf, data_meta)

    def _calc_meta_data(self, data, meta_conf):
        # type: (Any, ValueMetaConf) -> ValueMeta
        data_meta = None
        if data is not None and meta_conf is not None:
            # Combine meta_conf with the config settings
            try:
                data_meta = get_value_meta(
                    data, meta_conf, tracking_config=self.settings.tracking
                )
            except Exception as ex:
                log_exception(
                    "Error occurred during _calc_meta_data", ex, non_critical=True
                )

        if data_meta is None:
            data_meta = ValueMeta()

        return data_meta


def _get_dataset_name(operation_path, with_partition):
    """
    This is a temporary patch to report metrics with log_dataset.
    Should be removed in favor of reporting the metrics with the dataset operation
    """
    # todo: deprecate the name calculation from the sdk, move only to backend
    try:
        from urllib.parse import urlparse
    except ImportError:
        from urlparse import urlparse

    import itertools
    import os

    path = urlparse(str(operation_path)).path  # type: str

    if with_partition:
        dirname, basename = os.path.split(path)
        if "." in basename and not path.endswith("/"):
            path = dirname

    path_parts = path.strip("/").split("/")
    if with_partition:
        path_parts = list(itertools.takewhile(lambda part: "=" not in part, path_parts))

    dataset_name = ".".join(path_parts)

    # we might not successfully extract a name from the path so as a
    # fallback we return the original value
    if dataset_name == "":
        return operation_path

    return dataset_name


@attr.s(slots=True, frozen=False, kw_only=True)
class DatasetOperationReport(object):
    """
    Holds the information about an operation to report
    """

    op_path: Union[Target, str] = attr.ib()
    op_type: Union[DbndDatasetOperationType, str] = attr.ib(
        # convert str of "read" or "write" to operation type
        converter=lambda op_type: DbndDatasetOperationType[op_type]
        if isinstance(op_type, str)
        else op_type
    )
    with_preview: bool = attr.ib()
    with_schema: bool = attr.ib()

    data: Optional[Any] = attr.ib()
    with_histograms: Optional[Union[bool, str, List[str], LogDataRequest]] = attr.ib()
    with_stats: Optional[Union[bool, str, List[str], LogDataRequest]] = attr.ib()

    success: bool = attr.ib(default=True)
    error: Optional[str] = attr.ib(default=None)
    send_metrics = attr.ib(default=None)
    with_partition = attr.ib(default=None)
    row_count = attr.ib(default=None)
    column_count = attr.ib(default=None)

    meta_data: Optional[ValueMeta] = attr.ib(default=None)

    operation_source: Optional[str] = attr.ib(default=None)

    def set(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                logger.warning(
                    "Can't set attribute {} for DatasetOperationLogger, no such attribute".format(
                        k
                    )
                )

    def set_data(self, data):
        self.set(data=data)

    def set_metadata(self, metadata):
        self.set(meta_data=metadata)

    def set_error(self, error):
        # type: (str) -> None
        try:
            self.set(success=False, error=error)
        except Exception:
            # we don't print error, as the error might becaused by str(error)
            dbnd_log_exception("Failed to set error on dataset operation")

    def set_success(self):
        self.set(success=True)

    @property
    def meta_conf(self):
        return ValueMetaConf(
            log_preview=self.with_preview,
            log_schema=self.with_schema,
            log_size=self.with_schema,
            log_stats=self.with_stats,
            log_histograms=self.with_histograms,
        )

    @property
    def status(self):
        return (
            DbndTargetOperationStatus.OK
            if self.success
            else DbndTargetOperationStatus.NOK
        )
