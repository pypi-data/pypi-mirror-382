# © Copyright Databand.ai, an IBM Company 2022
import re

from dbnd._core.constants import TaskRunState
from dbnd._core.parameter.parameter_definition import ParameterGroup, _ParameterKind
from dbnd._core.tracking.schemas.base import ApiStrictSchema
from dbnd._core.tracking.schemas.tracking_info_objects import (
    TaskDefinitionInfo,
    TaskRunInfo,
    TaskRunParamInfo,
)
from dbnd._core.utils.data_anonymizers import (
    DEFAULT_MASKING_VALUE,
    SECRET_NAMES,
    mask_sensitive_data,
)
from dbnd._core.utils.dotdict import _as_dotted_dict
from dbnd._vendor._marshmallow import post_dump
from dbnd._vendor.marshmallow import fields, post_load
from dbnd._vendor.marshmallow_enum import EnumField


class TaskDefinitionParamSchema(ApiStrictSchema):
    """
    Based on TaskDefinitionParam object
    """

    name = fields.String()

    default = fields.String(allow_none=True)

    description = fields.String()

    group = EnumField(ParameterGroup)
    kind = EnumField(_ParameterKind)
    load_on_build = fields.Boolean()

    significant = fields.Boolean()
    value_type = fields.String()

    @post_load
    def make_task_definition_param(self, data, **kwargs):
        return _as_dotted_dict(**data)


class TaskDefinitionInfoSchema(ApiStrictSchema):
    task_definition_uid = fields.UUID()
    name = fields.String()

    class_version = fields.String()
    family = fields.String()

    module_source = fields.String(allow_none=True)
    module_source_hash = fields.String(allow_none=True)

    source = fields.String(allow_none=True)
    source_hash = fields.String(allow_none=True)

    type = fields.String()

    task_param_definitions = fields.Nested(TaskDefinitionParamSchema, many=True)

    @post_load
    def make_task_definition(self, data, **kwargs):
        return TaskDefinitionInfo(**data)


class TaskRunParamSchema(ApiStrictSchema):
    parameter_name = fields.String()
    value_origin = fields.String()
    value = fields.String(allow_none=True)

    def dump_value_safe(self, data: dict) -> str:
        parameter_name = data["parameter_name"]
        parameter_value = data["value"]

        matches = map(
            lambda secret_name: re.search(secret_name, parameter_name), SECRET_NAMES
        )

        if any(matches):
            return DEFAULT_MASKING_VALUE

        return mask_sensitive_data(parameter_value)

    @post_dump(pass_many=True)
    def mask_sensitive_values(self, data, many, **kwargs):
        if many:
            return [{**param, "value": self.dump_value_safe(param)} for param in data]

        return {**data, "value": self.dump_value_safe(data)}

    @post_load
    def make_task_run_param(self, data, **kwargs):
        return TaskRunParamInfo(**data)


class TaskRunInfoSchema(ApiStrictSchema):
    task_run_uid = fields.UUID()
    task_run_attempt_uid = fields.UUID()

    task_definition_uid = fields.UUID()
    run_uid = fields.UUID()
    task_id = fields.String()
    task_signature = fields.String()
    task_signature_source = fields.String()

    task_af_id = fields.String()
    execution_date = fields.DateTime(allow_none=True)

    name = fields.String()

    env = fields.String()

    command_line = fields.String()
    functional_call = fields.String()

    has_downstreams = fields.Boolean()
    has_upstreams = fields.Boolean()

    is_reused = fields.Boolean()
    is_dynamic = fields.Boolean()
    is_system = fields.Boolean()
    is_skipped = fields.Boolean()
    is_root = fields.Boolean()
    output_signature = fields.String()

    state = EnumField(TaskRunState)
    target_date = fields.Date(allow_none=True)

    log_local = fields.String(allow_none=True)
    log_remote = fields.String(allow_none=True)

    version = fields.String()

    task_run_params = fields.Nested(TaskRunParamSchema, many=True)

    external_links = fields.Dict(allow_none=True)

    @post_load
    def make_task_run(self, data, **kwargs):
        return TaskRunInfo(**data)
