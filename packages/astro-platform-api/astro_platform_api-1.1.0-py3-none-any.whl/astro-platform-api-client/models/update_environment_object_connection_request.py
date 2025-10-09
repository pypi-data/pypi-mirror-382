from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_environment_object_connection_request_extra import (
        UpdateEnvironmentObjectConnectionRequestExtra,
    )


T = TypeVar("T", bound="UpdateEnvironmentObjectConnectionRequest")


@_attrs_define
class UpdateEnvironmentObjectConnectionRequest:
    """
    Attributes:
        type_ (str): The type of connection
        auth_type_id (Union[Unset, str]): The ID for the connection auth type
        extra (Union[Unset, UpdateEnvironmentObjectConnectionRequestExtra]): Extra connection details, if any
        host (Union[Unset, str]): The host address for the connection
        login (Union[Unset, str]): The username used for the connection
        password (Union[Unset, str]): The password used for the connection
        port (Union[Unset, int]): The port for the connection
        schema (Union[Unset, str]): The schema for the connection
    """

    type_: str
    auth_type_id: Union[Unset, str] = UNSET
    extra: Union[Unset, "UpdateEnvironmentObjectConnectionRequestExtra"] = UNSET
    host: Union[Unset, str] = UNSET
    login: Union[Unset, str] = UNSET
    password: Union[Unset, str] = UNSET
    port: Union[Unset, int] = UNSET
    schema: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        auth_type_id = self.auth_type_id

        extra: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.extra, Unset):
            extra = self.extra.to_dict()

        host = self.host

        login = self.login

        password = self.password

        port = self.port

        schema = self.schema

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
            }
        )
        if auth_type_id is not UNSET:
            field_dict["authTypeId"] = auth_type_id
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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_environment_object_connection_request_extra import (
            UpdateEnvironmentObjectConnectionRequestExtra,
        )

        d = dict(src_dict)
        type_ = d.pop("type")

        auth_type_id = d.pop("authTypeId", UNSET)

        _extra = d.pop("extra", UNSET)
        extra: Union[Unset, UpdateEnvironmentObjectConnectionRequestExtra]
        if isinstance(_extra, Unset):
            extra = UNSET
        else:
            extra = UpdateEnvironmentObjectConnectionRequestExtra.from_dict(_extra)

        host = d.pop("host", UNSET)

        login = d.pop("login", UNSET)

        password = d.pop("password", UNSET)

        port = d.pop("port", UNSET)

        schema = d.pop("schema", UNSET)

        update_environment_object_connection_request = cls(
            type_=type_,
            auth_type_id=auth_type_id,
            extra=extra,
            host=host,
            login=login,
            password=password,
            port=port,
            schema=schema,
        )

        update_environment_object_connection_request.additional_properties = d
        return update_environment_object_connection_request

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
