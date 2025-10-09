from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.environment_object import EnvironmentObject


T = TypeVar("T", bound="EnvironmentObjectsPaginated")


@_attrs_define
class EnvironmentObjectsPaginated:
    """
    Attributes:
        environment_objects (list['EnvironmentObject']): The list of environment objects
        limit (int): The maximum number of environment objects in current page
        offset (int): The offset of the current page of environment objects
        total_count (int): The total number of environment objects
    """

    environment_objects: list["EnvironmentObject"]
    limit: int
    offset: int
    total_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        environment_objects = []
        for environment_objects_item_data in self.environment_objects:
            environment_objects_item = environment_objects_item_data.to_dict()
            environment_objects.append(environment_objects_item)

        limit = self.limit

        offset = self.offset

        total_count = self.total_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "environmentObjects": environment_objects,
                "limit": limit,
                "offset": offset,
                "totalCount": total_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.environment_object import EnvironmentObject

        d = dict(src_dict)
        environment_objects = []
        _environment_objects = d.pop("environmentObjects")
        for environment_objects_item_data in _environment_objects:
            environment_objects_item = EnvironmentObject.from_dict(environment_objects_item_data)

            environment_objects.append(environment_objects_item)

        limit = d.pop("limit")

        offset = d.pop("offset")

        total_count = d.pop("totalCount")

        environment_objects_paginated = cls(
            environment_objects=environment_objects,
            limit=limit,
            offset=offset,
            total_count=total_count,
        )

        environment_objects_paginated.additional_properties = d
        return environment_objects_paginated

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
