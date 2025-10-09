from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.environment_object_connection_overrides_extra import EnvironmentObjectConnectionOverridesExtra


T = TypeVar("T", bound="EnvironmentObjectConnectionOverrides")


@_attrs_define
class EnvironmentObjectConnectionOverrides:
    """
    Attributes:
        extra (Union[Unset, EnvironmentObjectConnectionOverridesExtra]): Extra connection details, if any
        host (Union[Unset, str]): The host address for the connection
        login (Union[Unset, str]): The username used for the connection
        password (Union[Unset, str]): The password used for the connection
        port (Union[Unset, int]): The port for the connection
        schema (Union[Unset, str]): The schema for the connection
        type_ (Union[Unset, str]): The type of connection
    """

    extra: Union[Unset, "EnvironmentObjectConnectionOverridesExtra"] = UNSET
    host: Union[Unset, str] = UNSET
    login: Union[Unset, str] = UNSET
    password: Union[Unset, str] = UNSET
    port: Union[Unset, int] = UNSET
    schema: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        extra: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.extra, Unset):
            extra = self.extra.to_dict()

        host = self.host

        login = self.login

        password = self.password

        port = self.port

        schema = self.schema

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if extra is not UNSET:
            field_dict["extra"] = extra
        if host is not UNSET:
            field_dict["host"] = host
        if login is not UNSET:
            field_dict["login"] = login
        if password is not UNSET:
            field_dict["password"] = password
        if port is not UNSET:
            field_dict["port"] = port
        if schema is not UNSET:
            field_dict["schema"] = schema
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.environment_object_connection_overrides_extra import EnvironmentObjectConnectionOverridesExtra

        d = dict(src_dict)
        _extra = d.pop("extra", UNSET)
        extra: Union[Unset, EnvironmentObjectConnectionOverridesExtra]
        if isinstance(_extra, Unset):
            extra = UNSET
        else:
            extra = EnvironmentObjectConnectionOverridesExtra.from_dict(_extra)

        host = d.pop("host", UNSET)

        login = d.pop("login", UNSET)

        password = d.pop("password", UNSET)

        port = d.pop("port", UNSET)

        schema = d.pop("schema", UNSET)

        type_ = d.pop("type", UNSET)

        environment_object_connection_overrides = cls(
            extra=extra,
            host=host,
            login=login,
            password=password,
            port=port,
            schema=schema,
            type_=type_,
        )

        environment_object_connection_overrides.additional_properties = d
        return environment_object_connection_overrides

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
