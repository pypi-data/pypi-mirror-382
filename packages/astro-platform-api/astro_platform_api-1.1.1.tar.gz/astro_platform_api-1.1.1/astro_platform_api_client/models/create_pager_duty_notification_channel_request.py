from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_pager_duty_notification_channel_request_entity_type import (
    CreatePagerDutyNotificationChannelRequestEntityType,
)
from ..models.create_pager_duty_notification_channel_request_type import CreatePagerDutyNotificationChannelRequestType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pager_duty_notification_channel_definition import PagerDutyNotificationChannelDefinition


T = TypeVar("T", bound="CreatePagerDutyNotificationChannelRequest")


@_attrs_define
class CreatePagerDutyNotificationChannelRequest:
    """
    Attributes:
        definition (PagerDutyNotificationChannelDefinition):
        entity_id (str): The entity ID the notification channel is scoped to.
        entity_type (CreatePagerDutyNotificationChannelRequestEntityType): The type of entity the notification channel
            is scoped to.
        name (str): The notification channel's name.
        type_ (CreatePagerDutyNotificationChannelRequestType): The notification channel's type.
        is_shared (Union[Unset, bool]): When entity type is scoped to ORGANIZATION or WORKSPACE, this determines if
            child entities can access this notification channel.
    """

    definition: "PagerDutyNotificationChannelDefinition"
    entity_id: str
    entity_type: CreatePagerDutyNotificationChannelRequestEntityType
    name: str
    type_: CreatePagerDutyNotificationChannelRequestType
    is_shared: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        definition = self.definition.to_dict()

        entity_id = self.entity_id

        entity_type = self.entity_type.value

        name = self.name

        type_ = self.type_.value

        is_shared = self.is_shared

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "definition": definition,
                "entityId": entity_id,
                "entityType": entity_type,
                "name": name,
                "type": type_,
            }
        )
        if is_shared is not UNSET:
            field_dict["isShared"] = is_shared

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pager_duty_notification_channel_definition import PagerDutyNotificationChannelDefinition

        d = dict(src_dict)
        definition = PagerDutyNotificationChannelDefinition.from_dict(d.pop("definition"))

        entity_id = d.pop("entityId")

        entity_type = CreatePagerDutyNotificationChannelRequestEntityType(d.pop("entityType"))

        name = d.pop("name")

        type_ = CreatePagerDutyNotificationChannelRequestType(d.pop("type"))

        is_shared = d.pop("isShared", UNSET)

        create_pager_duty_notification_channel_request = cls(
            definition=definition,
            entity_id=entity_id,
            entity_type=entity_type,
            name=name,
            type_=type_,
            is_shared=is_shared,
        )

        create_pager_duty_notification_channel_request.additional_properties = d
        return create_pager_duty_notification_channel_request

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
