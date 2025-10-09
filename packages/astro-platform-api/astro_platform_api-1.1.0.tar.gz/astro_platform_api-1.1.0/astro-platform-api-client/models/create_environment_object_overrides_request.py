from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_environment_object_airflow_variable_overrides_request import (
        CreateEnvironmentObjectAirflowVariableOverridesRequest,
    )
    from ..models.create_environment_object_connection_overrides_request import (
        CreateEnvironmentObjectConnectionOverridesRequest,
    )
    from ..models.create_environment_object_metrics_export_overrides_request import (
        CreateEnvironmentObjectMetricsExportOverridesRequest,
    )


T = TypeVar("T", bound="CreateEnvironmentObjectOverridesRequest")


@_attrs_define
class CreateEnvironmentObjectOverridesRequest:
    """
    Attributes:
        airflow_variable (Union[Unset, CreateEnvironmentObjectAirflowVariableOverridesRequest]):
        connection (Union[Unset, CreateEnvironmentObjectConnectionOverridesRequest]):
        metrics_export (Union[Unset, CreateEnvironmentObjectMetricsExportOverridesRequest]):
    """

    airflow_variable: Union[Unset, "CreateEnvironmentObjectAirflowVariableOverridesRequest"] = UNSET
    connection: Union[Unset, "CreateEnvironmentObjectConnectionOverridesRequest"] = UNSET
    metrics_export: Union[Unset, "CreateEnvironmentObjectMetricsExportOverridesRequest"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        airflow_variable: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.airflow_variable, Unset):
            airflow_variable = self.airflow_variable.to_dict()

        connection: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.connection, Unset):
            connection = self.connection.to_dict()

        metrics_export: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metrics_export, Unset):
            metrics_export = self.metrics_export.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if airflow_variable is not UNSET:
            field_dict["airflowVariable"] = airflow_variable
        if connection is not UNSET:
            field_dict["connection"] = connection
        if metrics_export is not UNSET:
            field_dict["metricsExport"] = metrics_export

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_environment_object_airflow_variable_overrides_request import (
            CreateEnvironmentObjectAirflowVariableOverridesRequest,
        )
        from ..models.create_environment_object_connection_overrides_request import (
            CreateEnvironmentObjectConnectionOverridesRequest,
        )
        from ..models.create_environment_object_metrics_export_overrides_request import (
            CreateEnvironmentObjectMetricsExportOverridesRequest,
        )

        d = dict(src_dict)
        _airflow_variable = d.pop("airflowVariable", UNSET)
        airflow_variable: Union[Unset, CreateEnvironmentObjectAirflowVariableOverridesRequest]
        if isinstance(_airflow_variable, Unset):
            airflow_variable = UNSET
        else:
            airflow_variable = CreateEnvironmentObjectAirflowVariableOverridesRequest.from_dict(_airflow_variable)

        _connection = d.pop("connection", UNSET)
        connection: Union[Unset, CreateEnvironmentObjectConnectionOverridesRequest]
        if isinstance(_connection, Unset):
            connection = UNSET
        else:
            connection = CreateEnvironmentObjectConnectionOverridesRequest.from_dict(_connection)

        _metrics_export = d.pop("metricsExport", UNSET)
        metrics_export: Union[Unset, CreateEnvironmentObjectMetricsExportOverridesRequest]
        if isinstance(_metrics_export, Unset):
            metrics_export = UNSET
        else:
            metrics_export = CreateEnvironmentObjectMetricsExportOverridesRequest.from_dict(_metrics_export)

        create_environment_object_overrides_request = cls(
            airflow_variable=airflow_variable,
            connection=connection,
            metrics_export=metrics_export,
        )

        create_environment_object_overrides_request.additional_properties = d
        return create_environment_object_overrides_request

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
