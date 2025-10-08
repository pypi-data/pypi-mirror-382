from enum import StrEnum
from typing import Any
from typing import Self

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import ValidationError
from pydantic import model_validator
from pydantic.alias_generators import to_camel
from pydantic_core import from_json

from .client import FirebaseRemoteConfigClient


class _BaseCamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
        serialize_by_alias=True,
    )


class RemoteConfigUpdateOrigin(StrEnum):
    ADMIN_SDK_NODE = "ADMIN_SDK_NODE"
    CONSOLE = "CONSOLE"
    REMOTE_CONFIG_UPDATE_ORIGIN_UNSPECIFIED = "REMOTE_CONFIG_UPDATE_ORIGIN_UNSPECIFIED"
    REST_API = "REST_API"


class RemoteConfigUpdateType(StrEnum):
    FORCED_UPDATE = "FORCED_UPDATE"
    INCREMENTAL_UPDATE = "INCREMENTAL_UPDATE"
    REMOTE_CONFIG_UPDATE_TYPE_UNSPECIFIED = "REMOTE_CONFIG_UPDATE_TYPE_UNSPECIFIED"
    ROLLBACK = "ROLLBACK"


class RemoteConfigUpdateUser(BaseModel):
    email: EmailStr

    image_url: str | None = None
    name: str | None = None


class RemoteConfigValueType(StrEnum):
    BOOLEAN = "BOOLEAN"
    JSON = "JSON"
    NUMBER = "NUMBER"
    PARAMETER_VALUE_TYPE_UNSPECIFIED = "PARAMETER_VALUE_TYPE_UNSPECIFIED"
    STRING = "STRING"


class RemoteConfigVersion(_BaseCamelModel):
    update_origin: RemoteConfigUpdateOrigin
    update_time: str
    update_type: RemoteConfigUpdateType
    update_user: RemoteConfigUpdateUser
    version_number: int

    is_legacy: bool = False
    rollback_source: str | None = None


class _RemoteConfigDefaultValue(_BaseCamelModel):
    value: Any


class _RemoteConfigParameter(_BaseCamelModel):
    # TODO: implement conditional value.
    default_value: _RemoteConfigDefaultValue
    value_type: RemoteConfigValueType

    conditional_values: Any = None
    description: str | None = None


class _RemoteConfigParameterGroup(_BaseCamelModel):
    parameters: dict[str, _RemoteConfigParameter]

    description: str | None = None


class _RemoteConfig(_BaseCamelModel):
    version: RemoteConfigVersion

    parameters: dict[str, _RemoteConfigParameter] | None = None
    parameter_groups: dict[str, _RemoteConfigParameterGroup] | None = None

    @model_validator(mode="after")
    def ensure_have_parameters(self) -> Self:
        if self.parameters is None and self.parameter_groups is None:
            raise ValueError("Missing both `parameters` and `parameterGroups`")
        return self


class RemoteConfigConfigDict(ConfigDict, total=False):
    rc_group: str | None
    rc_nested_delimiter: str | None
    rc_prefix: str | None


class BaseRemoteConfigModel(BaseModel):
    """
    TBD
    """

    model_config = RemoteConfigConfigDict()

    rc_version: RemoteConfigVersion

    @classmethod
    def _build_field_values(
        cls, parameters: dict[str, _RemoteConfigParameter]
    ) -> dict[str, Any]:
        fields: dict[str, Any] = dict()
        rc_nested_delimiter: str | None = cls.model_config.get("rc_nested_delimiter")
        rc_prefix: str | None = cls.model_config.get("rc_prefix")
        for key, parameter in parameters.items():
            field_name = key
            if rc_prefix is not None and field_name.startswith(rc_prefix):
                field_name = field_name[len(rc_prefix) :]
            if parameter.value_type == RemoteConfigValueType.JSON:
                fields[field_name] = from_json(parameter.default_value.value)
                continue
            if rc_nested_delimiter is None:
                fields[field_name] = parameter.default_value.value
            else:
                path = field_name.split(rc_nested_delimiter)
                ptr = 0
                current = fields
                while ptr < len(path):
                    if path[ptr] not in current:
                        if ptr == len(path) - 1:
                            current[path[ptr]] = parameter.default_value.value
                        else:
                            current[path[ptr]] = dict()
                    if ptr != len(path) - 1:
                        current = current[path[ptr]]
                    ptr += 1
        return fields

    @classmethod
    async def model_validate_remoteconfig(
        cls,
        *,
        rc_client: FirebaseRemoteConfigClient | None = None,
    ) -> Self:
        if rc_client is None:
            rc_client = FirebaseRemoteConfigClient.from_environment()
        template = await rc_client.get_server_remote_template()
        rc = _RemoteConfig(**template)
        rc_group: str | None = cls.model_config.get("rc_group")
        parameters = rc.parameters
        if rc_group:
            if rc.parameter_groups is None:
                raise ValidationError(f"No parameter group found remotely")
            parameter_group = rc.parameter_groups.get(rc_group)
            if parameter_group is None:
                raise ValidationError(f"Unknown remote parameter group {rc_group}")
            parameters = parameter_group.parameters
        if parameters is None:
            raise ValidationError(f"Unknown remote parameter group {rc_group}")
        return cls(
            rc_version=rc.version,
            **cls._build_field_values(parameters),
        )
