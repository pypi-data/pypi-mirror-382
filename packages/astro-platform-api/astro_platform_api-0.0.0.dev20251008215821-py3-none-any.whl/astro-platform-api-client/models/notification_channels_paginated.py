from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.notification_channel import NotificationChannel


T = TypeVar("T", bound="NotificationChannelsPaginated")


@_attrs_define
class NotificationChannelsPaginated:
    """
    Attributes:
        limit (int): The maximum number of notification channels to return.
        notification_channels (list['NotificationChannel']): The notification channels.
        offset (int): The offset of the first notification channel in the list.
        total_count (int): The total number of notification channels.
    """

    limit: int
    notification_channels: list["NotificationChannel"]
    offset: int
    total_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        limit = self.limit

        notification_channels = []
        for notification_channels_item_data in self.notification_channels:
            notification_channels_item = notification_channels_item_data.to_dict()
            notification_channels.append(notification_channels_item)

        offset = self.offset

        total_count = self.total_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "limit": limit,
                "notificationChannels": notification_channels,
                "offset": offset,
                "totalCount": total_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.notification_channel import NotificationChannel

        d = dict(src_dict)
        limit = d.pop("limit")

        notification_channels = []
        _notification_channels = d.pop("notificationChannels")
        for notification_channels_item_data in _notification_channels:
            notification_channels_item = NotificationChannel.from_dict(notification_channels_item_data)

            notification_channels.append(notification_channels_item)

        offset = d.pop("offset")

        total_count = d.pop("totalCount")

        notification_channels_paginated = cls(
            limit=limit,
            notification_channels=notification_channels,
            offset=offset,
            total_count=total_count,
        )

        notification_channels_paginated.additional_properties = d
        return notification_channels_paginated

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
