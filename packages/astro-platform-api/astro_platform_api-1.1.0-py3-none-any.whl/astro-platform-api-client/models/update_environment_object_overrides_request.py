from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_environment_object_airflow_variable_overrides_request import (
        UpdateEnvironmentObjectAirflowVariableOverridesRequest,
    )
    from ..models.update_environment_object_connection_overrides_request import (
        UpdateEnvironmentObjectConnectionOverridesRequest,
    )
    from ..models.update_environment_object_metrics_export_overrides_request import (
        UpdateEnvironmentObjectMetricsExportOverridesRequest,
    )


T = TypeVar("T", bound="UpdateEnvironmentObjectOverridesRequest")


@_attrs_define
class UpdateEnvironmentObjectOverridesRequest:
    """
    Attributes:
        airflow_variable (Union[Unset, UpdateEnvironmentObjectAirflowVariableOverridesRequest]):
        connection (Union[Unset, UpdateEnvironmentObjectConnectionOverridesRequest]):
        metrics_export (Union[Unset, UpdateEnvironmentObjectMetricsExportOverridesRequest]):
    """

    airflow_variable: Union[Unset, "UpdateEnvironmentObjectAirflowVariableOverridesRequest"] = UNSET
    connection: Union[Unset, "UpdateEnvironmentObjectConnectionOverridesRequest"] = UNSET
    metrics_export: Union[Unset, "UpdateEnvironmentObjectMetricsExportOverridesRequest"] = UNSET
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
        from ..models.update_environment_object_airflow_variable_overrides_request import (
            UpdateEnvironmentObjectAirflowVariableOverridesRequest,
        )
        from ..models.update_environment_object_connection_overrides_request import (
            UpdateEnvironmentObjectConnectionOverridesRequest,
        )
        from ..models.update_environment_object_metrics_export_overrides_request import (
            UpdateEnvironmentObjectMetricsExportOverridesRequest,
        )

        d = dict(src_dict)
        _airflow_variable = d.pop("airflowVariable", UNSET)
        airflow_variable: Union[Unset, UpdateEnvironmentObjectAirflowVariableOverridesRequest]
        if isinstance(_airflow_variable, Unset):
            airflow_variable = UNSET
        else:
            airflow_variable = UpdateEnvironmentObjectAirflowVariableOverridesRequest.from_dict(_airflow_variable)

        _connection = d.pop("connection", UNSET)
        connection: Union[Unset, UpdateEnvironmentObjectConnectionOverridesRequest]
        if isinstance(_connection, Unset):
            connection = UNSET
        else:
            connection = UpdateEnvironmentObjectConnectionOverridesRequest.from_dict(_connection)

        _metrics_export = d.pop("metricsExport", UNSET)
        metrics_export: Union[Unset, UpdateEnvironmentObjectMetricsExportOverridesRequest]
        if isinstance(_metrics_export, Unset):
            metrics_export = UNSET
        else:
            metrics_export = UpdateEnvironmentObjectMetricsExportOverridesRequest.from_dict(_metrics_export)

        update_environment_object_overrides_request = cls(
            airflow_variable=airflow_variable,
            connection=connection,
            metrics_export=metrics_export,
        )

        update_environment_object_overrides_request.additional_properties = d
        return update_environment_object_overrides_request

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
