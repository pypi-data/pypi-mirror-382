from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.alert_notification_channel_entity_type import AlertNotificationChannelEntityType
from ..models.alert_notification_channel_type import AlertNotificationChannelType
from ..types import UNSET, Unset

T = TypeVar("T", bound="AlertNotificationChannel")


@_attrs_define
class AlertNotificationChannel:
    """
    Attributes:
        created_at (str): The time when the notification channel was created in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`.
        definition (Any): The definition of the notification.
        entity_id (str): The ID of the entity the notification channel is associated with.
        entity_type (AlertNotificationChannelEntityType): The type of entity the notification channel is associated
            with.
        id (str): The ID of the notification channel.
        name (str): The name of the notification channel.
        organization_id (str): The ID of the organization the notification channel is associated with.
        type_ (AlertNotificationChannelType): The type of the notification channel.
        updated_at (str): The time when the notification channel was last updated in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`.
        deployment_id (Union[Unset, str]): The ID of the deployment the notification channel is associated with.
        workspace_id (Union[Unset, str]): The ID of the workspace the notification channel is associated with.
    """

    created_at: str
    definition: Any
    entity_id: str
    entity_type: AlertNotificationChannelEntityType
    id: str
    name: str
    organization_id: str
    type_: AlertNotificationChannelType
    updated_at: str
    deployment_id: Union[Unset, str] = UNSET
    workspace_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at

        definition = self.definition

        entity_id = self.entity_id

        entity_type = self.entity_type.value

        id = self.id

        name = self.name

        organization_id = self.organization_id

        type_ = self.type_.value

        updated_at = self.updated_at

        deployment_id = self.deployment_id

        workspace_id = self.workspace_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "createdAt": created_at,
                "definition": definition,
                "entityId": entity_id,
                "entityType": entity_type,
                "id": id,
                "name": name,
                "organizationId": organization_id,
                "type": type_,
                "updatedAt": updated_at,
            }
        )
        if deployment_id is not UNSET:
            field_dict["deploymentId"] = deployment_id
        if workspace_id is not UNSET:
            field_dict["workspaceId"] = workspace_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_at = d.pop("createdAt")

        definition = d.pop("definition")

        entity_id = d.pop("entityId")

        entity_type = AlertNotificationChannelEntityType(d.pop("entityType"))

        id = d.pop("id")

        name = d.pop("name")

        organization_id = d.pop("organizationId")

        type_ = AlertNotificationChannelType(d.pop("type"))

        updated_at = d.pop("updatedAt")

        deployment_id = d.pop("deploymentId", UNSET)

        workspace_id = d.pop("workspaceId", UNSET)

        alert_notification_channel = cls(
            created_at=created_at,
            definition=definition,
            entity_id=entity_id,
            entity_type=entity_type,
            id=id,
            name=name,
            organization_id=organization_id,
            type_=type_,
            updated_at=updated_at,
            deployment_id=deployment_id,
            workspace_id=workspace_id,
        )

        alert_notification_channel.additional_properties = d
        return alert_notification_channel

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
