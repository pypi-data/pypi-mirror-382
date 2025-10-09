from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.alert import Alert


T = TypeVar("T", bound="AlertsPaginated")


@_attrs_define
class AlertsPaginated:
    """
    Attributes:
        alerts (list['Alert']): The list of alerts.
        limit (int): The limit for pagination.
        offset (int): The offset for pagination.
        total_count (int): The total count of alerts.
    """

    alerts: list["Alert"]
    limit: int
    offset: int
    total_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        alerts = []
        for alerts_item_data in self.alerts:
            alerts_item = alerts_item_data.to_dict()
            alerts.append(alerts_item)

        limit = self.limit

        offset = self.offset

        total_count = self.total_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "alerts": alerts,
                "limit": limit,
                "offset": offset,
                "totalCount": total_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.alert import Alert

        d = dict(src_dict)
        alerts = []
        _alerts = d.pop("alerts")
        for alerts_item_data in _alerts:
            alerts_item = Alert.from_dict(alerts_item_data)

            alerts.append(alerts_item)

        limit = d.pop("limit")

        offset = d.pop("offset")

        total_count = d.pop("totalCount")

        alerts_paginated = cls(
            alerts=alerts,
            limit=limit,
            offset=offset,
            total_count=total_count,
        )

        alerts_paginated.additional_properties = d
        return alerts_paginated

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
