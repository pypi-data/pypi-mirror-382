from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.basic_subject_profile import BasicSubjectProfile


T = TypeVar("T", bound="NotificationChannel")


@_attrs_define
class NotificationChannel:
    """
    Attributes:
        created_at (str): The time when the alert was created in UTC, formatted as `YYYY-MM-DDTHH:MM:SSZ`.
        created_by (BasicSubjectProfile):
        definition (Any): The notification channel's definition.
        entity_id (str): The entity ID the notification channel is scoped to.
        entity_type (str): The type of entity the notification channel is scoped to.
        id (str): The notification channel's ID.
        is_shared (bool): When entity type is scoped to ORGANIZATION or WORKSPACE, this determines if child entities can
            access this notification channel.
        name (str): The notification channel's name.
        organization_id (str): The organization ID the notification channel is scoped to.
        type_ (str): The notification channel's type.
        updated_at (str): The time when the alert was updated in UTC, formatted as `YYYY-MM-DDTHH:MM:SSZ`.
        updated_by (BasicSubjectProfile):
        deployment_id (Union[Unset, str]): The deployment ID the notification channel is scoped to.
        entity_name (Union[Unset, str]): The name of the entity the notification channel is scoped to.
        workspace_id (Union[Unset, str]): The workspace ID the notification channel is scoped to.
    """

    created_at: str
    created_by: "BasicSubjectProfile"
    definition: Any
    entity_id: str
    entity_type: str
    id: str
    is_shared: bool
    name: str
    organization_id: str
    type_: str
    updated_at: str
    updated_by: "BasicSubjectProfile"
    deployment_id: Union[Unset, str] = UNSET
    entity_name: Union[Unset, str] = UNSET
    workspace_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at

        created_by = self.created_by.to_dict()

        definition = self.definition

        entity_id = self.entity_id

        entity_type = self.entity_type

        id = self.id

        is_shared = self.is_shared

        name = self.name

        organization_id = self.organization_id

        type_ = self.type_

        updated_at = self.updated_at

        updated_by = self.updated_by.to_dict()

        deployment_id = self.deployment_id

        entity_name = self.entity_name

        workspace_id = self.workspace_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "createdAt": created_at,
                "createdBy": created_by,
                "definition": definition,
                "entityId": entity_id,
                "entityType": entity_type,
                "id": id,
                "isShared": is_shared,
                "name": name,
                "organizationId": organization_id,
                "type": type_,
                "updatedAt": updated_at,
                "updatedBy": updated_by,
            }
        )
        if deployment_id is not UNSET:
            field_dict["deploymentId"] = deployment_id
        if entity_name is not UNSET:
            field_dict["entityName"] = entity_name
        if workspace_id is not UNSET:
            field_dict["workspaceId"] = workspace_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.basic_subject_profile import BasicSubjectProfile

        d = dict(src_dict)
        created_at = d.pop("createdAt")

        created_by = BasicSubjectProfile.from_dict(d.pop("createdBy"))

        definition = d.pop("definition")

        entity_id = d.pop("entityId")

        entity_type = d.pop("entityType")

        id = d.pop("id")

        is_shared = d.pop("isShared")

        name = d.pop("name")

        organization_id = d.pop("organizationId")

        type_ = d.pop("type")

        updated_at = d.pop("updatedAt")

        updated_by = BasicSubjectProfile.from_dict(d.pop("updatedBy"))

        deployment_id = d.pop("deploymentId", UNSET)

        entity_name = d.pop("entityName", UNSET)

        workspace_id = d.pop("workspaceId", UNSET)

        notification_channel = cls(
            created_at=created_at,
            created_by=created_by,
            definition=definition,
            entity_id=entity_id,
            entity_type=entity_type,
            id=id,
            is_shared=is_shared,
            name=name,
            organization_id=organization_id,
            type_=type_,
            updated_at=updated_at,
            updated_by=updated_by,
            deployment_id=deployment_id,
            entity_name=entity_name,
            workspace_id=workspace_id,
        )

        notification_channel.additional_properties = d
        return notification_channel

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
