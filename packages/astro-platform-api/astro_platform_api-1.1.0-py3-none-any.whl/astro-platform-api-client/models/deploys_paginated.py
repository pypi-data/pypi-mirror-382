from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.deploy import Deploy


T = TypeVar("T", bound="DeploysPaginated")


@_attrs_define
class DeploysPaginated:
    """
    Attributes:
        deploys (list['Deploy']): A list of deploys in the current page.
        limit (int): The maximum number of deploys in one page.
        offset (int): The offset of the current page of deploys.
        total_count (int): The total number of deploys.
    """

    deploys: list["Deploy"]
    limit: int
    offset: int
    total_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        deploys = []
        for deploys_item_data in self.deploys:
            deploys_item = deploys_item_data.to_dict()
            deploys.append(deploys_item)

        limit = self.limit

        offset = self.offset

        total_count = self.total_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "deploys": deploys,
                "limit": limit,
                "offset": offset,
                "totalCount": total_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.deploy import Deploy

        d = dict(src_dict)
        deploys = []
        _deploys = d.pop("deploys")
        for deploys_item_data in _deploys:
            deploys_item = Deploy.from_dict(deploys_item_data)

            deploys.append(deploys_item)

        limit = d.pop("limit")

        offset = d.pop("offset")

        total_count = d.pop("totalCount")

        deploys_paginated = cls(
            deploys=deploys,
            limit=limit,
            offset=offset,
            total_count=total_count,
        )

        deploys_paginated.additional_properties = d
        return deploys_paginated

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
