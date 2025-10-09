from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_environment_object_metrics_export_overrides_request_auth_type import (
    CreateEnvironmentObjectMetricsExportOverridesRequestAuthType,
)
from ..models.create_environment_object_metrics_export_overrides_request_exporter_type import (
    CreateEnvironmentObjectMetricsExportOverridesRequestExporterType,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_environment_object_metrics_export_overrides_request_headers import (
        CreateEnvironmentObjectMetricsExportOverridesRequestHeaders,
    )
    from ..models.create_environment_object_metrics_export_overrides_request_labels import (
        CreateEnvironmentObjectMetricsExportOverridesRequestLabels,
    )


T = TypeVar("T", bound="CreateEnvironmentObjectMetricsExportOverridesRequest")


@_attrs_define
class CreateEnvironmentObjectMetricsExportOverridesRequest:
    """
    Attributes:
        auth_type (Union[Unset, CreateEnvironmentObjectMetricsExportOverridesRequestAuthType]): The type of
            authentication to use when connecting to the remote endpoint
        basic_token (Union[Unset, str]): The bearer token to connect to the remote endpoint
        endpoint (Union[Unset, str]): The Prometheus endpoint where the metrics are exported
        exporter_type (Union[Unset, CreateEnvironmentObjectMetricsExportOverridesRequestExporterType]): The type of
            exporter
        headers (Union[Unset, CreateEnvironmentObjectMetricsExportOverridesRequestHeaders]): Add key-value pairs to the
            HTTP request headers made by Astro when connecting to the remote endpoint
        labels (Union[Unset, CreateEnvironmentObjectMetricsExportOverridesRequestLabels]): Any key-value pair metrics
            labels for your export. You can use these to filter your metrics in downstream applications.
        password (Union[Unset, str]): The password to connect to the remote endpoint
        username (Union[Unset, str]): The username to connect to the remote endpoint
    """

    auth_type: Union[Unset, CreateEnvironmentObjectMetricsExportOverridesRequestAuthType] = UNSET
    basic_token: Union[Unset, str] = UNSET
    endpoint: Union[Unset, str] = UNSET
    exporter_type: Union[Unset, CreateEnvironmentObjectMetricsExportOverridesRequestExporterType] = UNSET
    headers: Union[Unset, "CreateEnvironmentObjectMetricsExportOverridesRequestHeaders"] = UNSET
    labels: Union[Unset, "CreateEnvironmentObjectMetricsExportOverridesRequestLabels"] = UNSET
    password: Union[Unset, str] = UNSET
    username: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        auth_type: Union[Unset, str] = UNSET
        if not isinstance(self.auth_type, Unset):
            auth_type = self.auth_type.value

        basic_token = self.basic_token

        endpoint = self.endpoint

        exporter_type: Union[Unset, str] = UNSET
        if not isinstance(self.exporter_type, Unset):
            exporter_type = self.exporter_type.value

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
        field_dict.update({})
        if auth_type is not UNSET:
            field_dict["authType"] = auth_type
        if basic_token is not UNSET:
            field_dict["basicToken"] = basic_token
        if endpoint is not UNSET:
            field_dict["endpoint"] = endpoint
        if exporter_type is not UNSET:
            field_dict["exporterType"] = exporter_type
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
        from ..models.create_environment_object_metrics_export_overrides_request_headers import (
            CreateEnvironmentObjectMetricsExportOverridesRequestHeaders,
        )
        from ..models.create_environment_object_metrics_export_overrides_request_labels import (
            CreateEnvironmentObjectMetricsExportOverridesRequestLabels,
        )

        d = dict(src_dict)
        _auth_type = d.pop("authType", UNSET)
        auth_type: Union[Unset, CreateEnvironmentObjectMetricsExportOverridesRequestAuthType]
        if isinstance(_auth_type, Unset):
            auth_type = UNSET
        else:
            auth_type = CreateEnvironmentObjectMetricsExportOverridesRequestAuthType(_auth_type)

        basic_token = d.pop("basicToken", UNSET)

        endpoint = d.pop("endpoint", UNSET)

        _exporter_type = d.pop("exporterType", UNSET)
        exporter_type: Union[Unset, CreateEnvironmentObjectMetricsExportOverridesRequestExporterType]
        if isinstance(_exporter_type, Unset):
            exporter_type = UNSET
        else:
            exporter_type = CreateEnvironmentObjectMetricsExportOverridesRequestExporterType(_exporter_type)

        _headers = d.pop("headers", UNSET)
        headers: Union[Unset, CreateEnvironmentObjectMetricsExportOverridesRequestHeaders]
        if isinstance(_headers, Unset):
            headers = UNSET
        else:
            headers = CreateEnvironmentObjectMetricsExportOverridesRequestHeaders.from_dict(_headers)

        _labels = d.pop("labels", UNSET)
        labels: Union[Unset, CreateEnvironmentObjectMetricsExportOverridesRequestLabels]
        if isinstance(_labels, Unset):
            labels = UNSET
        else:
            labels = CreateEnvironmentObjectMetricsExportOverridesRequestLabels.from_dict(_labels)

        password = d.pop("password", UNSET)

        username = d.pop("username", UNSET)

        create_environment_object_metrics_export_overrides_request = cls(
            auth_type=auth_type,
            basic_token=basic_token,
            endpoint=endpoint,
            exporter_type=exporter_type,
            headers=headers,
            labels=labels,
            password=password,
            username=username,
        )

        create_environment_object_metrics_export_overrides_request.additional_properties = d
        return create_environment_object_metrics_export_overrides_request

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
