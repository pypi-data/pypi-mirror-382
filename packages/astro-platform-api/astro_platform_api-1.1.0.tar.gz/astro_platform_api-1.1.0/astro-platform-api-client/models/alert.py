import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.alert_entity_type import AlertEntityType
from ..models.alert_severity import AlertSeverity
from ..models.alert_type import AlertType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.alert_notification_channel import AlertNotificationChannel
    from ..models.alert_rules import AlertRules
    from ..models.basic_subject_profile import BasicSubjectProfile


T = TypeVar("T", bound="Alert")


@_attrs_define
class Alert:
    """
    Attributes:
        created_at (datetime.datetime): The time when the alert was created in UTC, formatted as `YYYY-MM-DDTHH:MM:SSZ`.
            Example: 2022-11-22T04:37:12Z.
        created_by (BasicSubjectProfile):
        entity_id (str): The ID of the entity the alert is associated with.
        entity_type (AlertEntityType): The type of entity the alert is associated with.
        id (str): The alert's ID.
        name (str): The alert's name.
        organization_id (str): The ID of the organization the alert is associated with.
        rules (AlertRules):
        severity (AlertSeverity): The alert's severity.
        type_ (AlertType): The alert's type.
        updated_at (datetime.datetime): The time when the alert was last updated in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        updated_by (BasicSubjectProfile):
        deployment_id (Union[Unset, str]): The ID of the deployment the alert is associated with.
        entity_name (Union[Unset, str]): The name of the entity the alert is associated with.
        notification_channels (Union[Unset, list['AlertNotificationChannel']]): The notification channels to send alerts
            to.
        workspace_id (Union[Unset, str]): The ID of the workspace the alert is associated with.
    """

    created_at: datetime.datetime
    created_by: "BasicSubjectProfile"
    entity_id: str
    entity_type: AlertEntityType
    id: str
    name: str
    organization_id: str
    rules: "AlertRules"
    severity: AlertSeverity
    type_: AlertType
    updated_at: datetime.datetime
    updated_by: "BasicSubjectProfile"
    deployment_id: Union[Unset, str] = UNSET
    entity_name: Union[Unset, str] = UNSET
    notification_channels: Union[Unset, list["AlertNotificationChannel"]] = UNSET
    workspace_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at.isoformat()

        created_by = self.created_by.to_dict()

        entity_id = self.entity_id

        entity_type = self.entity_type.value

        id = self.id

        name = self.name

        organization_id = self.organization_id

        rules = self.rules.to_dict()

        severity = self.severity.value

        type_ = self.type_.value

        updated_at = self.updated_at.isoformat()

        updated_by = self.updated_by.to_dict()

        deployment_id = self.deployment_id

        entity_name = self.entity_name

        notification_channels: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.notification_channels, Unset):
            notification_channels = []
            for notification_channels_item_data in self.notification_channels:
                notification_channels_item = notification_channels_item_data.to_dict()
                notification_channels.append(notification_channels_item)

        workspace_id = self.workspace_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "createdAt": created_at,
                "createdBy": created_by,
                "entityId": entity_id,
                "entityType": entity_type,
                "id": id,
                "name": name,
                "organizationId": organization_id,
                "rules": rules,
                "severity": severity,
                "type": type_,
                "updatedAt": updated_at,
                "updatedBy": updated_by,
            }
        )
        if deployment_id is not UNSET:
            field_dict["deploymentId"] = deployment_id
        if entity_name is not UNSET:
            field_dict["entityName"] = entity_name
        if notification_channels is not UNSET:
            field_dict["notificationChannels"] = notification_channels
        if workspace_id is not UNSET:
            field_dict["workspaceId"] = workspace_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.alert_notification_channel import AlertNotificationChannel
        from ..models.alert_rules import AlertRules
        from ..models.basic_subject_profile import BasicSubjectProfile

        d = dict(src_dict)
        created_at = isoparse(d.pop("createdAt"))

        created_by = BasicSubjectProfile.from_dict(d.pop("createdBy"))

        entity_id = d.pop("entityId")

        entity_type = AlertEntityType(d.pop("entityType"))

        id = d.pop("id")

        name = d.pop("name")

        organization_id = d.pop("organizationId")

        rules = AlertRules.from_dict(d.pop("rules"))

        severity = AlertSeverity(d.pop("severity"))

        type_ = AlertType(d.pop("type"))

        updated_at = isoparse(d.pop("updatedAt"))

        updated_by = BasicSubjectProfile.from_dict(d.pop("updatedBy"))

        deployment_id = d.pop("deploymentId", UNSET)

        entity_name = d.pop("entityName", UNSET)

        notification_channels = []
        _notification_channels = d.pop("notificationChannels", UNSET)
        for notification_channels_item_data in _notification_channels or []:
            notification_channels_item = AlertNotificationChannel.from_dict(notification_channels_item_data)

            notification_channels.append(notification_channels_item)

        workspace_id = d.pop("workspaceId", UNSET)

        alert = cls(
            created_at=created_at,
            created_by=created_by,
            entity_id=entity_id,
            entity_type=entity_type,
            id=id,
            name=name,
            organization_id=organization_id,
            rules=rules,
            severity=severity,
            type_=type_,
            updated_at=updated_at,
            updated_by=updated_by,
            deployment_id=deployment_id,
            entity_name=entity_name,
            notification_channels=notification_channels,
            workspace_id=workspace_id,
        )

        alert.additional_properties = d
        return alert

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
