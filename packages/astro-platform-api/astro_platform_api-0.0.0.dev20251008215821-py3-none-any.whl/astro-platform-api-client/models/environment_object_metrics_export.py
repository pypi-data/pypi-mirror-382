from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.environment_object_metrics_export_auth_type import EnvironmentObjectMetricsExportAuthType
from ..models.environment_object_metrics_export_exporter_type import EnvironmentObjectMetricsExportExporterType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.environment_object_metrics_export_headers import EnvironmentObjectMetricsExportHeaders
    from ..models.environment_object_metrics_export_labels import EnvironmentObjectMetricsExportLabels


T = TypeVar("T", bound="EnvironmentObjectMetricsExport")


@_attrs_define
class EnvironmentObjectMetricsExport:
    """
    Attributes:
        endpoint (str): The Prometheus endpoint where the metrics are exported
        exporter_type (EnvironmentObjectMetricsExportExporterType): The type of exporter
        auth_type (Union[Unset, EnvironmentObjectMetricsExportAuthType]): The type of authentication to use when
            connecting to the remote endpoint
        basic_token (Union[Unset, str]): The bearer token to connect to the remote endpoint
        headers (Union[Unset, EnvironmentObjectMetricsExportHeaders]): Add key-value pairs to the HTTP request headers
            made by Astro when connecting to the remote endpoint
        labels (Union[Unset, EnvironmentObjectMetricsExportLabels]): Any key-value pair metrics labels for your export.
            You can use these to filter your metrics in downstream applications.
        password (Union[Unset, str]): The password to connect to the remote endpoint
        username (Union[Unset, str]): The username to connect to the remote endpoint
    """

    endpoint: str
    exporter_type: EnvironmentObjectMetricsExportExporterType
    auth_type: Union[Unset, EnvironmentObjectMetricsExportAuthType] = UNSET
    basic_token: Union[Unset, str] = UNSET
    headers: Union[Unset, "EnvironmentObjectMetricsExportHeaders"] = UNSET
    labels: Union[Unset, "EnvironmentObjectMetricsExportLabels"] = UNSET
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
        from ..models.environment_object_metrics_export_headers import EnvironmentObjectMetricsExportHeaders
        from ..models.environment_object_metrics_export_labels import EnvironmentObjectMetricsExportLabels

        d = dict(src_dict)
        endpoint = d.pop("endpoint")

        exporter_type = EnvironmentObjectMetricsExportExporterType(d.pop("exporterType"))

        _auth_type = d.pop("authType", UNSET)
        auth_type: Union[Unset, EnvironmentObjectMetricsExportAuthType]
        if isinstance(_auth_type, Unset):
            auth_type = UNSET
        else:
            auth_type = EnvironmentObjectMetricsExportAuthType(_auth_type)

        basic_token = d.pop("basicToken", UNSET)

        _headers = d.pop("headers", UNSET)
        headers: Union[Unset, EnvironmentObjectMetricsExportHeaders]
        if isinstance(_headers, Unset):
            headers = UNSET
        else:
            headers = EnvironmentObjectMetricsExportHeaders.from_dict(_headers)

        _labels = d.pop("labels", UNSET)
        labels: Union[Unset, EnvironmentObjectMetricsExportLabels]
        if isinstance(_labels, Unset):
            labels = UNSET
        else:
            labels = EnvironmentObjectMetricsExportLabels.from_dict(_labels)

        password = d.pop("password", UNSET)

        username = d.pop("username", UNSET)

        environment_object_metrics_export = cls(
            endpoint=endpoint,
            exporter_type=exporter_type,
            auth_type=auth_type,
            basic_token=basic_token,
            headers=headers,
            labels=labels,
            password=password,
            username=username,
        )

        environment_object_metrics_export.additional_properties = d
        return environment_object_metrics_export

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
