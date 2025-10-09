from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.environment_object_metrics_export_overrides_auth_type import (
    EnvironmentObjectMetricsExportOverridesAuthType,
)
from ..models.environment_object_metrics_export_overrides_exporter_type import (
    EnvironmentObjectMetricsExportOverridesExporterType,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.environment_object_metrics_export_overrides_headers import (
        EnvironmentObjectMetricsExportOverridesHeaders,
    )
    from ..models.environment_object_metrics_export_overrides_labels import (
        EnvironmentObjectMetricsExportOverridesLabels,
    )


T = TypeVar("T", bound="EnvironmentObjectMetricsExportOverrides")


@_attrs_define
class EnvironmentObjectMetricsExportOverrides:
    """
    Attributes:
        auth_type (Union[Unset, EnvironmentObjectMetricsExportOverridesAuthType]): The type of authentication to use
            when connecting to the remote endpoint
        basic_token (Union[Unset, str]): The bearer token to connect to the remote endpoint
        endpoint (Union[Unset, str]): The Prometheus endpoint where the metrics are exported
        exporter_type (Union[Unset, EnvironmentObjectMetricsExportOverridesExporterType]): The type of exporter
        headers (Union[Unset, EnvironmentObjectMetricsExportOverridesHeaders]): Add key-value pairs to the HTTP request
            headers made by Astro when connecting to the remote endpoint
        labels (Union[Unset, EnvironmentObjectMetricsExportOverridesLabels]): Any key-value pair metrics labels for your
            export. You can use these to filter your metrics in downstream applications.
        password (Union[Unset, str]): The password to connect to the remote endpoint
        username (Union[Unset, str]): The username to connect to the remote endpoint
    """

    auth_type: Union[Unset, EnvironmentObjectMetricsExportOverridesAuthType] = UNSET
    basic_token: Union[Unset, str] = UNSET
    endpoint: Union[Unset, str] = UNSET
    exporter_type: Union[Unset, EnvironmentObjectMetricsExportOverridesExporterType] = UNSET
    headers: Union[Unset, "EnvironmentObjectMetricsExportOverridesHeaders"] = UNSET
    labels: Union[Unset, "EnvironmentObjectMetricsExportOverridesLabels"] = UNSET
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
        from ..models.environment_object_metrics_export_overrides_headers import (
            EnvironmentObjectMetricsExportOverridesHeaders,
        )
        from ..models.environment_object_metrics_export_overrides_labels import (
            EnvironmentObjectMetricsExportOverridesLabels,
        )

        d = dict(src_dict)
        _auth_type = d.pop("authType", UNSET)
        auth_type: Union[Unset, EnvironmentObjectMetricsExportOverridesAuthType]
        if isinstance(_auth_type, Unset):
            auth_type = UNSET
        else:
            auth_type = EnvironmentObjectMetricsExportOverridesAuthType(_auth_type)

        basic_token = d.pop("basicToken", UNSET)

        endpoint = d.pop("endpoint", UNSET)

        _exporter_type = d.pop("exporterType", UNSET)
        exporter_type: Union[Unset, EnvironmentObjectMetricsExportOverridesExporterType]
        if isinstance(_exporter_type, Unset):
            exporter_type = UNSET
        else:
            exporter_type = EnvironmentObjectMetricsExportOverridesExporterType(_exporter_type)

        _headers = d.pop("headers", UNSET)
        headers: Union[Unset, EnvironmentObjectMetricsExportOverridesHeaders]
        if isinstance(_headers, Unset):
            headers = UNSET
        else:
            headers = EnvironmentObjectMetricsExportOverridesHeaders.from_dict(_headers)

        _labels = d.pop("labels", UNSET)
        labels: Union[Unset, EnvironmentObjectMetricsExportOverridesLabels]
        if isinstance(_labels, Unset):
            labels = UNSET
        else:
            labels = EnvironmentObjectMetricsExportOverridesLabels.from_dict(_labels)

        password = d.pop("password", UNSET)

        username = d.pop("username", UNSET)

        environment_object_metrics_export_overrides = cls(
            auth_type=auth_type,
            basic_token=basic_token,
            endpoint=endpoint,
            exporter_type=exporter_type,
            headers=headers,
            labels=labels,
            password=password,
            username=username,
        )

        environment_object_metrics_export_overrides.additional_properties = d
        return environment_object_metrics_export_overrides

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
