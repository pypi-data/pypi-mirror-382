from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.environment_object_link_scope import EnvironmentObjectLinkScope
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.environment_object_airflow_variable_overrides import EnvironmentObjectAirflowVariableOverrides
    from ..models.environment_object_connection_overrides import EnvironmentObjectConnectionOverrides
    from ..models.environment_object_metrics_export_overrides import EnvironmentObjectMetricsExportOverrides


T = TypeVar("T", bound="EnvironmentObjectLink")


@_attrs_define
class EnvironmentObjectLink:
    """
    Attributes:
        scope (EnvironmentObjectLinkScope): Scope of the linked entity for the environment object
        scope_entity_id (str): Linked entity ID the environment object
        airflow_variable_overrides (Union[Unset, EnvironmentObjectAirflowVariableOverrides]):
        connection_overrides (Union[Unset, EnvironmentObjectConnectionOverrides]):
        metrics_export_overrides (Union[Unset, EnvironmentObjectMetricsExportOverrides]):
    """

    scope: EnvironmentObjectLinkScope
    scope_entity_id: str
    airflow_variable_overrides: Union[Unset, "EnvironmentObjectAirflowVariableOverrides"] = UNSET
    connection_overrides: Union[Unset, "EnvironmentObjectConnectionOverrides"] = UNSET
    metrics_export_overrides: Union[Unset, "EnvironmentObjectMetricsExportOverrides"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        scope = self.scope.value

        scope_entity_id = self.scope_entity_id

        airflow_variable_overrides: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.airflow_variable_overrides, Unset):
            airflow_variable_overrides = self.airflow_variable_overrides.to_dict()

        connection_overrides: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.connection_overrides, Unset):
            connection_overrides = self.connection_overrides.to_dict()

        metrics_export_overrides: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metrics_export_overrides, Unset):
            metrics_export_overrides = self.metrics_export_overrides.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "scope": scope,
                "scopeEntityId": scope_entity_id,
            }
        )
        if airflow_variable_overrides is not UNSET:
            field_dict["airflowVariableOverrides"] = airflow_variable_overrides
        if connection_overrides is not UNSET:
            field_dict["connectionOverrides"] = connection_overrides
        if metrics_export_overrides is not UNSET:
            field_dict["metricsExportOverrides"] = metrics_export_overrides

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.environment_object_airflow_variable_overrides import EnvironmentObjectAirflowVariableOverrides
        from ..models.environment_object_connection_overrides import EnvironmentObjectConnectionOverrides
        from ..models.environment_object_metrics_export_overrides import EnvironmentObjectMetricsExportOverrides

        d = dict(src_dict)
        scope = EnvironmentObjectLinkScope(d.pop("scope"))

        scope_entity_id = d.pop("scopeEntityId")

        _airflow_variable_overrides = d.pop("airflowVariableOverrides", UNSET)
        airflow_variable_overrides: Union[Unset, EnvironmentObjectAirflowVariableOverrides]
        if isinstance(_airflow_variable_overrides, Unset):
            airflow_variable_overrides = UNSET
        else:
            airflow_variable_overrides = EnvironmentObjectAirflowVariableOverrides.from_dict(
                _airflow_variable_overrides
            )

        _connection_overrides = d.pop("connectionOverrides", UNSET)
        connection_overrides: Union[Unset, EnvironmentObjectConnectionOverrides]
        if isinstance(_connection_overrides, Unset):
            connection_overrides = UNSET
        else:
            connection_overrides = EnvironmentObjectConnectionOverrides.from_dict(_connection_overrides)

        _metrics_export_overrides = d.pop("metricsExportOverrides", UNSET)
        metrics_export_overrides: Union[Unset, EnvironmentObjectMetricsExportOverrides]
        if isinstance(_metrics_export_overrides, Unset):
            metrics_export_overrides = UNSET
        else:
            metrics_export_overrides = EnvironmentObjectMetricsExportOverrides.from_dict(_metrics_export_overrides)

        environment_object_link = cls(
            scope=scope,
            scope_entity_id=scope_entity_id,
            airflow_variable_overrides=airflow_variable_overrides,
            connection_overrides=connection_overrides,
            metrics_export_overrides=metrics_export_overrides,
        )

        environment_object_link.additional_properties = d
        return environment_object_link

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
