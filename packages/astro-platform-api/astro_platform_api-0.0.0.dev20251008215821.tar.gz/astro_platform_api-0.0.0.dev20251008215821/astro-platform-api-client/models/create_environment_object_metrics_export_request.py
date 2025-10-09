from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_environment_object_metrics_export_request_auth_type import (
    CreateEnvironmentObjectMetricsExportRequestAuthType,
)
from ..models.create_environment_object_metrics_export_request_exporter_type import (
    CreateEnvironmentObjectMetricsExportRequestExporterType,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_environment_object_metrics_export_request_headers import (
        CreateEnvironmentObjectMetricsExportRequestHeaders,
    )
    from ..models.create_environment_object_metrics_export_request_labels import (
        CreateEnvironmentObjectMetricsExportRequestLabels,
    )


T = TypeVar("T", bound="CreateEnvironmentObjectMetricsExportRequest")


@_attrs_define
class CreateEnvironmentObjectMetricsExportRequest:
    """
    Attributes:
        endpoint (str): The Prometheus endpoint where the metrics are exported
        exporter_type (CreateEnvironmentObjectMetricsExportRequestExporterType): The type of exporter
        auth_type (Union[Unset, CreateEnvironmentObjectMetricsExportRequestAuthType]): The type of authentication to use
            when connecting to the remote endpoint
        basic_token (Union[Unset, str]): The bearer token to connect to the remote endpoint
        headers (Union[Unset, CreateEnvironmentObjectMetricsExportRequestHeaders]): Add key-value pairs to the HTTP
            request headers made by Astro when connecting to the remote endpoint
        labels (Union[Unset, CreateEnvironmentObjectMetricsExportRequestLabels]): Any key-value pair metrics labels for
            your export. You can use these to filter your metrics in downstream applications.
        password (Union[Unset, str]): The password to connect to the remote endpoint
        username (Union[Unset, str]): The username to connect to the remote endpoint
    """

    endpoint: str
    exporter_type: CreateEnvironmentObjectMetricsExportRequestExporterType
    auth_type: Union[Unset, CreateEnvironmentObjectMetricsExportRequestAuthType] = UNSET
    basic_token: Union[Unset, str] = UNSET
    headers: Union[Unset, "CreateEnvironmentObjectMetricsExportRequestHeaders"] = UNSET
    labels: Union[Unset, "CreateEnvironmentObjectMetricsExportRequestLabels"] = UNSET
    password: Union[Unset, str] = UNSET
    username: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        endpoint = self.endpoint

        exporter_type = self.exporter_type.value

        auth_type: Union[Unset, str] = UNSET
        if not isinstance(self.auth_type, Unset):
            auth_type = self.auth_type.value

        basic_token = self.basic_token

        headers: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.headers, Unset):
            headers = self.headers.to_dict()

        labels: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels.to_dict()

        password = self.password

        username = self.username

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "endpoint": endpoint,
                "exporterType": exporter_type,
            }
        )
        if auth_type is not UNSET:
            field_dict["authType"] = auth_type
        if basic_token is not UNSET:
            field_dict["basicToken"] = basic_token
        if headers is not UNSET:
            field_dict["headers"] = headers
        if labels is not UNSET:
            field_dict["labels"] = labels
        if password is not UNSET:
            field_dict["password"] = password
        if username is not UNSET:
            field_dict["username"] = username

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_environment_object_metrics_export_request_headers import (
            CreateEnvironmentObjectMetricsExportRequestHeaders,
        )
        from ..models.create_environment_object_metrics_export_request_labels import (
            CreateEnvironmentObjectMetricsExportRequestLabels,
        )

        d = dict(src_dict)
        endpoint = d.pop("endpoint")

        exporter_type = CreateEnvironmentObjectMetricsExportRequestExporterType(d.pop("exporterType"))

        _auth_type = d.pop("authType", UNSET)
        auth_type: Union[Unset, CreateEnvironmentObjectMetricsExportRequestAuthType]
        if isinstance(_auth_type, Unset):
            auth_type = UNSET
        else:
            auth_type = CreateEnvironmentObjectMetricsExportRequestAuthType(_auth_type)

        basic_token = d.pop("basicToken", UNSET)

        _headers = d.pop("headers", UNSET)
        headers: Union[Unset, CreateEnvironmentObjectMetricsExportRequestHeaders]
        if isinstance(_headers, Unset):
            headers = UNSET
        else:
            headers = CreateEnvironmentObjectMetricsExportRequestHeaders.from_dict(_headers)

        _labels = d.pop("labels", UNSET)
        labels: Union[Unset, CreateEnvironmentObjectMetricsExportRequestLabels]
        if isinstance(_labels, Unset):
            labels = UNSET
        else:
            labels = CreateEnvironmentObjectMetricsExportRequestLabels.from_dict(_labels)

        password = d.pop("password", UNSET)

        username = d.pop("username", UNSET)

        create_environment_object_metrics_export_request = cls(
            endpoint=endpoint,
            exporter_type=exporter_type,
            auth_type=auth_type,
            basic_token=basic_token,
            headers=headers,
            labels=labels,
            password=password,
            username=username,
        )

        create_environment_object_metrics_export_request.additional_properties = d
        return create_environment_object_metrics_export_request

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
