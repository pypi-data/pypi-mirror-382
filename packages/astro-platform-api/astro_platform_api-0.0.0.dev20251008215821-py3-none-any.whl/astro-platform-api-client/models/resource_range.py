from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ResourceRange")


@_attrs_define
class ResourceRange:
    """
    Attributes:
        ceiling (str): The maximum value. Example: 10.
        default (str): The default value. Example: 5.
        floor (str): The minimum value. Example: 1.
    """

    ceiling: str
    default: str
    floor: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ceiling = self.ceiling

        default = self.default

        floor = self.floor

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ceiling": ceiling,
                "default": default,
                "floor": floor,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ceiling = d.pop("ceiling")

        default = d.pop("default")

        floor = d.pop("floor")

        resource_range = cls(
            ceiling=ceiling,
            default=default,
            floor=floor,
        )

        resource_range.additional_properties = d
        return resource_range

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
