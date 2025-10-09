from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.organization import Organization


T = TypeVar("T", bound="OrganizationsPaginated")


@_attrs_define
class OrganizationsPaginated:
    """
    Attributes:
        limit (int): The maximum number of Organizations in the page. Example: 10.
        offset (int): The offset of the Organizations in the page.
        organizations (list['Organization']): The list of Organizations in the page.
        total_count (int): The total number of Organizations. Example: 100.
    """

    limit: int
    offset: int
    organizations: list["Organization"]
    total_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        limit = self.limit

        offset = self.offset

        organizations = []
        for organizations_item_data in self.organizations:
            organizations_item = organizations_item_data.to_dict()
            organizations.append(organizations_item)

        total_count = self.total_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "limit": limit,
                "offset": offset,
                "organizations": organizations,
                "totalCount": total_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.organization import Organization

        d = dict(src_dict)
        limit = d.pop("limit")

        offset = d.pop("offset")

        organizations = []
        _organizations = d.pop("organizations")
        for organizations_item_data in _organizations:
            organizations_item = Organization.from_dict(organizations_item_data)

            organizations.append(organizations_item)

        total_count = d.pop("totalCount")

        organizations_paginated = cls(
            limit=limit,
            offset=offset,
            organizations=organizations,
            total_count=total_count,
        )

        organizations_paginated.additional_properties = d
        return organizations_paginated

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
