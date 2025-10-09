from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_environment_object_request_object_type import CreateEnvironmentObjectRequestObjectType
from ..models.create_environment_object_request_scope import CreateEnvironmentObjectRequestScope
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_environment_object_airflow_variable_request import (
        CreateEnvironmentObjectAirflowVariableRequest,
    )
    from ..models.create_environment_object_connection_request import CreateEnvironmentObjectConnectionRequest
    from ..models.create_environment_object_link_request import CreateEnvironmentObjectLinkRequest
    from ..models.create_environment_object_metrics_export_request import CreateEnvironmentObjectMetricsExportRequest
    from ..models.exclude_link_environment_object_request import ExcludeLinkEnvironmentObjectRequest


T = TypeVar("T", bound="CreateEnvironmentObjectRequest")


@_attrs_define
class CreateEnvironmentObjectRequest:
    """
    Attributes:
        object_key (str): The key for the environment object
        object_type (CreateEnvironmentObjectRequestObjectType): The type of environment object
        scope (CreateEnvironmentObjectRequestScope): The scope of the environment object
        scope_entity_id (str): The ID of the scope entity where the environment object is created
        airflow_variable (Union[Unset, CreateEnvironmentObjectAirflowVariableRequest]):
        auto_link_deployments (Union[Unset, bool]): Whether or not to automatically link Deployments to the environment
            object. Only applicable for WORKSPACE scope
        connection (Union[Unset, CreateEnvironmentObjectConnectionRequest]):
        exclude_links (Union[Unset, list['ExcludeLinkEnvironmentObjectRequest']]): The links to exclude from the
            environment object. Only applicable for WORKSPACE scope
        links (Union[Unset, list['CreateEnvironmentObjectLinkRequest']]): The Deployments that Astro links to the
            environment object. Only applicable for WORKSPACE scope
        metrics_export (Union[Unset, CreateEnvironmentObjectMetricsExportRequest]):
    """

    object_key: str
    object_type: CreateEnvironmentObjectRequestObjectType
    scope: CreateEnvironmentObjectRequestScope
    scope_entity_id: str
    airflow_variable: Union[Unset, "CreateEnvironmentObjectAirflowVariableRequest"] = UNSET
    auto_link_deployments: Union[Unset, bool] = UNSET
    connection: Union[Unset, "CreateEnvironmentObjectConnectionRequest"] = UNSET
    exclude_links: Union[Unset, list["ExcludeLinkEnvironmentObjectRequest"]] = UNSET
    links: Union[Unset, list["CreateEnvironmentObjectLinkRequest"]] = UNSET
    metrics_export: Union[Unset, "CreateEnvironmentObjectMetricsExportRequest"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        object_key = self.object_key

        object_type = self.object_type.value

        scope = self.scope.value

        scope_entity_id = self.scope_entity_id

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
        field_dict.update(
            {
                "objectKey": object_key,
                "objectType": object_type,
                "scope": scope,
                "scopeEntityId": scope_entity_id,
            }
        )
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
        from ..models.create_environment_object_airflow_variable_request import (
            CreateEnvironmentObjectAirflowVariableRequest,
        )
        from ..models.create_environment_object_connection_request import CreateEnvironmentObjectConnectionRequest
        from ..models.create_environment_object_link_request import CreateEnvironmentObjectLinkRequest
        from ..models.create_environment_object_metrics_export_request import (
            CreateEnvironmentObjectMetricsExportRequest,
        )
        from ..models.exclude_link_environment_object_request import ExcludeLinkEnvironmentObjectRequest

        d = dict(src_dict)
        object_key = d.pop("objectKey")

        object_type = CreateEnvironmentObjectRequestObjectType(d.pop("objectType"))

        scope = CreateEnvironmentObjectRequestScope(d.pop("scope"))

        scope_entity_id = d.pop("scopeEntityId")

        _airflow_variable = d.pop("airflowVariable", UNSET)
        airflow_variable: Union[Unset, CreateEnvironmentObjectAirflowVariableRequest]
        if isinstance(_airflow_variable, Unset):
            airflow_variable = UNSET
        else:
            airflow_variable = CreateEnvironmentObjectAirflowVariableRequest.from_dict(_airflow_variable)

        auto_link_deployments = d.pop("autoLinkDeployments", UNSET)

        _connection = d.pop("connection", UNSET)
        connection: Union[Unset, CreateEnvironmentObjectConnectionRequest]
        if isinstance(_connection, Unset):
            connection = UNSET
        else:
            connection = CreateEnvironmentObjectConnectionRequest.from_dict(_connection)

        exclude_links = []
        _exclude_links = d.pop("excludeLinks", UNSET)
        for exclude_links_item_data in _exclude_links or []:
            exclude_links_item = ExcludeLinkEnvironmentObjectRequest.from_dict(exclude_links_item_data)

            exclude_links.append(exclude_links_item)

        links = []
        _links = d.pop("links", UNSET)
        for links_item_data in _links or []:
            links_item = CreateEnvironmentObjectLinkRequest.from_dict(links_item_data)

            links.append(links_item)

        _metrics_export = d.pop("metricsExport", UNSET)
        metrics_export: Union[Unset, CreateEnvironmentObjectMetricsExportRequest]
        if isinstance(_metrics_export, Unset):
            metrics_export = UNSET
        else:
            metrics_export = CreateEnvironmentObjectMetricsExportRequest.from_dict(_metrics_export)

        create_environment_object_request = cls(
            object_key=object_key,
            object_type=object_type,
            scope=scope,
            scope_entity_id=scope_entity_id,
            airflow_variable=airflow_variable,
            auto_link_deployments=auto_link_deployments,
            connection=connection,
            exclude_links=exclude_links,
            links=links,
            metrics_export=metrics_export,
        )

        create_environment_object_request.additional_properties = d
        return create_environment_object_request

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
