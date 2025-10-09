from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.exclude_link_environment_object_request import ExcludeLinkEnvironmentObjectRequest
    from ..models.update_environment_object_airflow_variable_request import (
        UpdateEnvironmentObjectAirflowVariableRequest,
    )
    from ..models.update_environment_object_connection_request import UpdateEnvironmentObjectConnectionRequest
    from ..models.update_environment_object_link_request import UpdateEnvironmentObjectLinkRequest
    from ..models.update_environment_object_metrics_export_request import UpdateEnvironmentObjectMetricsExportRequest


T = TypeVar("T", bound="UpdateEnvironmentObjectRequest")


@_attrs_define
class UpdateEnvironmentObjectRequest:
    """
    Attributes:
        airflow_variable (Union[Unset, UpdateEnvironmentObjectAirflowVariableRequest]):
        auto_link_deployments (Union[Unset, bool]): Whether or not to automatically link Deployments to the environment
            object. Only applicable for WORKSPACE scope
        connection (Union[Unset, UpdateEnvironmentObjectConnectionRequest]):
        exclude_links (Union[Unset, list['ExcludeLinkEnvironmentObjectRequest']]): The links to exclude from the
            environment object. Only applicable for WORKSPACE scope
        links (Union[Unset, list['UpdateEnvironmentObjectLinkRequest']]): The Deployments that Astro links to the
            environment object. Only applicable for WORKSPACE scope
        metrics_export (Union[Unset, UpdateEnvironmentObjectMetricsExportRequest]):
    """

    airflow_variable: Union[Unset, "UpdateEnvironmentObjectAirflowVariableRequest"] = UNSET
    auto_link_deployments: Union[Unset, bool] = UNSET
    connection: Union[Unset, "UpdateEnvironmentObjectConnectionRequest"] = UNSET
    exclude_links: Union[Unset, list["ExcludeLinkEnvironmentObjectRequest"]] = UNSET
    links: Union[Unset, list["UpdateEnvironmentObjectLinkRequest"]] = UNSET
    metrics_export: Union[Unset, "UpdateEnvironmentObjectMetricsExportRequest"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        airflow_variable: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.airflow_variable, Unset):
            airflow_variable = self.airflow_variable.to_dict()

        auto_link_deployments = self.auto_link_deployments

        connection: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.connection, Unset):
            connection = self.connection.to_dict()

        exclude_links: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.exclude_links, Unset):
            exclude_links = []
            for exclude_links_item_data in self.exclude_links:
                exclude_links_item = exclude_links_item_data.to_dict()
                exclude_links.append(exclude_links_item)

        links: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.links, Unset):
            links = []
            for links_item_data in self.links:
                links_item = links_item_data.to_dict()
                links.append(links_item)

        metrics_export: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metrics_export, Unset):
            metrics_export = self.metrics_export.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if airflow_variable is not UNSET:
            field_dict["airflowVariable"] = airflow_variable
        if auto_link_deployments is not UNSET:
            field_dict["autoLinkDeployments"] = auto_link_deployments
        if connection is not UNSET:
            field_dict["connection"] = connection
        if exclude_links is not UNSET:
            field_dict["excludeLinks"] = exclude_links
        if links is not UNSET:
            field_dict["links"] = links
        if metrics_export is not UNSET:
            field_dict["metricsExport"] = metrics_export

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.exclude_link_environment_object_request import ExcludeLinkEnvironmentObjectRequest
        from ..models.update_environment_object_airflow_variable_request import (
            UpdateEnvironmentObjectAirflowVariableRequest,
        )
        from ..models.update_environment_object_connection_request import UpdateEnvironmentObjectConnectionRequest
        from ..models.update_environment_object_link_request import UpdateEnvironmentObjectLinkRequest
        from ..models.update_environment_object_metrics_export_request import (
            UpdateEnvironmentObjectMetricsExportRequest,
        )

        d = dict(src_dict)
        _airflow_variable = d.pop("airflowVariable", UNSET)
        airflow_variable: Union[Unset, UpdateEnvironmentObjectAirflowVariableRequest]
        if isinstance(_airflow_variable, Unset):
            airflow_variable = UNSET
        else:
            airflow_variable = UpdateEnvironmentObjectAirflowVariableRequest.from_dict(_airflow_variable)

        auto_link_deployments = d.pop("autoLinkDeployments", UNSET)

        _connection = d.pop("connection", UNSET)
        connection: Union[Unset, UpdateEnvironmentObjectConnectionRequest]
        if isinstance(_connection, Unset):
            connection = UNSET
        else:
            connection = UpdateEnvironmentObjectConnectionRequest.from_dict(_connection)

        exclude_links = []
        _exclude_links = d.pop("excludeLinks", UNSET)
        for exclude_links_item_data in _exclude_links or []:
            exclude_links_item = ExcludeLinkEnvironmentObjectRequest.from_dict(exclude_links_item_data)

            exclude_links.append(exclude_links_item)

        links = []
        _links = d.pop("links", UNSET)
        for links_item_data in _links or []:
            links_item = UpdateEnvironmentObjectLinkRequest.from_dict(links_item_data)

            links.append(links_item)

        _metrics_export = d.pop("metricsExport", UNSET)
        metrics_export: Union[Unset, UpdateEnvironmentObjectMetricsExportRequest]
        if isinstance(_metrics_export, Unset):
            metrics_export = UNSET
        else:
            metrics_export = UpdateEnvironmentObjectMetricsExportRequest.from_dict(_metrics_export)

        update_environment_object_request = cls(
            airflow_variable=airflow_variable,
            auto_link_deployments=auto_link_deployments,
            connection=connection,
            exclude_links=exclude_links,
            links=links,
            metrics_export=metrics_export,
        )

        update_environment_object_request.additional_properties = d
        return update_environment_object_request

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
