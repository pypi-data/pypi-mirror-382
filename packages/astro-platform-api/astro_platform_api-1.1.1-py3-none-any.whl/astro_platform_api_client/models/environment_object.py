from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.environment_object_object_type import EnvironmentObjectObjectType
from ..models.environment_object_scope import EnvironmentObjectScope
from ..models.environment_object_source_scope import EnvironmentObjectSourceScope
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.basic_subject_profile import BasicSubjectProfile
    from ..models.environment_object_airflow_variable import EnvironmentObjectAirflowVariable
    from ..models.environment_object_connection import EnvironmentObjectConnection
    from ..models.environment_object_exclude_link import EnvironmentObjectExcludeLink
    from ..models.environment_object_link import EnvironmentObjectLink
    from ..models.environment_object_metrics_export import EnvironmentObjectMetricsExport


T = TypeVar("T", bound="EnvironmentObject")


@_attrs_define
class EnvironmentObject:
    """
    Attributes:
        object_key (str): The key for the environment object
        object_type (EnvironmentObjectObjectType): The type of environment object
        scope (EnvironmentObjectScope): The scope of the environment object
        scope_entity_id (str): The ID of the scope entity where the environment object is created
        airflow_variable (Union[Unset, EnvironmentObjectAirflowVariable]):
        auto_link_deployments (Union[Unset, bool]): Whether or not to automatically link Deployments to the environment
            object
        connection (Union[Unset, EnvironmentObjectConnection]):
        created_at (Union[Unset, str]): The time when the environment object was created in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`
        created_by (Union[Unset, BasicSubjectProfile]):
        exclude_links (Union[Unset, list['EnvironmentObjectExcludeLink']]): The excluded links for the environment
            object
        id (Union[Unset, str]): The ID of the environment object
        links (Union[Unset, list['EnvironmentObjectLink']]): The Deployments linked to the environment object
        metrics_export (Union[Unset, EnvironmentObjectMetricsExport]):
        source_scope (Union[Unset, EnvironmentObjectSourceScope]): The source scope of the environment object, if it is
            resolved from a link
        source_scope_entity_id (Union[Unset, str]): The source scope entity ID of the environment object, if it is
            resolved from a link
        updated_at (Union[Unset, str]): The time when the environment object was updated in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`
        updated_by (Union[Unset, BasicSubjectProfile]):
    """

    object_key: str
    object_type: EnvironmentObjectObjectType
    scope: EnvironmentObjectScope
    scope_entity_id: str
    airflow_variable: Union[Unset, "EnvironmentObjectAirflowVariable"] = UNSET
    auto_link_deployments: Union[Unset, bool] = UNSET
    connection: Union[Unset, "EnvironmentObjectConnection"] = UNSET
    created_at: Union[Unset, str] = UNSET
    created_by: Union[Unset, "BasicSubjectProfile"] = UNSET
    exclude_links: Union[Unset, list["EnvironmentObjectExcludeLink"]] = UNSET
    id: Union[Unset, str] = UNSET
    links: Union[Unset, list["EnvironmentObjectLink"]] = UNSET
    metrics_export: Union[Unset, "EnvironmentObjectMetricsExport"] = UNSET
    source_scope: Union[Unset, EnvironmentObjectSourceScope] = UNSET
    source_scope_entity_id: Union[Unset, str] = UNSET
    updated_at: Union[Unset, str] = UNSET
    updated_by: Union[Unset, "BasicSubjectProfile"] = UNSET
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

        created_at = self.created_at

        created_by: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.created_by, Unset):
            created_by = self.created_by.to_dict()

        exclude_links: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.exclude_links, Unset):
            exclude_links = []
            for exclude_links_item_data in self.exclude_links:
                exclude_links_item = exclude_links_item_data.to_dict()
                exclude_links.append(exclude_links_item)

        id = self.id

        links: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.links, Unset):
            links = []
            for links_item_data in self.links:
                links_item = links_item_data.to_dict()
                links.append(links_item)

        metrics_export: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metrics_export, Unset):
            metrics_export = self.metrics_export.to_dict()

        source_scope: Union[Unset, str] = UNSET
        if not isinstance(self.source_scope, Unset):
            source_scope = self.source_scope.value

        source_scope_entity_id = self.source_scope_entity_id

        updated_at = self.updated_at

        updated_by: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.updated_by, Unset):
            updated_by = self.updated_by.to_dict()

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
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if exclude_links is not UNSET:
            field_dict["excludeLinks"] = exclude_links
        if id is not UNSET:
            field_dict["id"] = id
        if links is not UNSET:
            field_dict["links"] = links
        if metrics_export is not UNSET:
            field_dict["metricsExport"] = metrics_export
        if source_scope is not UNSET:
            field_dict["sourceScope"] = source_scope
        if source_scope_entity_id is not UNSET:
            field_dict["sourceScopeEntityId"] = source_scope_entity_id
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at
        if updated_by is not UNSET:
            field_dict["updatedBy"] = updated_by

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.basic_subject_profile import BasicSubjectProfile
        from ..models.environment_object_airflow_variable import EnvironmentObjectAirflowVariable
        from ..models.environment_object_connection import EnvironmentObjectConnection
        from ..models.environment_object_exclude_link import EnvironmentObjectExcludeLink
        from ..models.environment_object_link import EnvironmentObjectLink
        from ..models.environment_object_metrics_export import EnvironmentObjectMetricsExport

        d = dict(src_dict)
        object_key = d.pop("objectKey")

        object_type = EnvironmentObjectObjectType(d.pop("objectType"))

        scope = EnvironmentObjectScope(d.pop("scope"))

        scope_entity_id = d.pop("scopeEntityId")

        _airflow_variable = d.pop("airflowVariable", UNSET)
        airflow_variable: Union[Unset, EnvironmentObjectAirflowVariable]
        if isinstance(_airflow_variable, Unset):
            airflow_variable = UNSET
        else:
            airflow_variable = EnvironmentObjectAirflowVariable.from_dict(_airflow_variable)

        auto_link_deployments = d.pop("autoLinkDeployments", UNSET)

        _connection = d.pop("connection", UNSET)
        connection: Union[Unset, EnvironmentObjectConnection]
        if isinstance(_connection, Unset):
            connection = UNSET
        else:
            connection = EnvironmentObjectConnection.from_dict(_connection)

        created_at = d.pop("createdAt", UNSET)

        _created_by = d.pop("createdBy", UNSET)
        created_by: Union[Unset, BasicSubjectProfile]
        if isinstance(_created_by, Unset):
            created_by = UNSET
        else:
            created_by = BasicSubjectProfile.from_dict(_created_by)

        exclude_links = []
        _exclude_links = d.pop("excludeLinks", UNSET)
        for exclude_links_item_data in _exclude_links or []:
            exclude_links_item = EnvironmentObjectExcludeLink.from_dict(exclude_links_item_data)

            exclude_links.append(exclude_links_item)

        id = d.pop("id", UNSET)

        links = []
        _links = d.pop("links", UNSET)
        for links_item_data in _links or []:
            links_item = EnvironmentObjectLink.from_dict(links_item_data)

            links.append(links_item)

        _metrics_export = d.pop("metricsExport", UNSET)
        metrics_export: Union[Unset, EnvironmentObjectMetricsExport]
        if isinstance(_metrics_export, Unset):
            metrics_export = UNSET
        else:
            metrics_export = EnvironmentObjectMetricsExport.from_dict(_metrics_export)

        _source_scope = d.pop("sourceScope", UNSET)
        source_scope: Union[Unset, EnvironmentObjectSourceScope]
        if isinstance(_source_scope, Unset):
            source_scope = UNSET
        else:
            source_scope = EnvironmentObjectSourceScope(_source_scope)

        source_scope_entity_id = d.pop("sourceScopeEntityId", UNSET)

        updated_at = d.pop("updatedAt", UNSET)

        _updated_by = d.pop("updatedBy", UNSET)
        updated_by: Union[Unset, BasicSubjectProfile]
        if isinstance(_updated_by, Unset):
            updated_by = UNSET
        else:
            updated_by = BasicSubjectProfile.from_dict(_updated_by)

        environment_object = cls(
            object_key=object_key,
            object_type=object_type,
            scope=scope,
            scope_entity_id=scope_entity_id,
            airflow_variable=airflow_variable,
            auto_link_deployments=auto_link_deployments,
            connection=connection,
            created_at=created_at,
            created_by=created_by,
            exclude_links=exclude_links,
            id=id,
            links=links,
            metrics_export=metrics_export,
            source_scope=source_scope,
            source_scope_entity_id=source_scope_entity_id,
            updated_at=updated_at,
            updated_by=updated_by,
        )

        environment_object.additional_properties = d
        return environment_object

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
