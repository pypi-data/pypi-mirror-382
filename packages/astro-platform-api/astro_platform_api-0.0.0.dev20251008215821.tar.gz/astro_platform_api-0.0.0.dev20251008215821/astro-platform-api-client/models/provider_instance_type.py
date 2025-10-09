from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ProviderInstanceType")


@_attrs_define
class ProviderInstanceType:
    """
    Attributes:
        cpu (int): The number of CPUs. Units are in number of CPU cores. Example: 4.
        memory (str): The amount of memory. Units in Gibibytes or `Gi`. Example: 16Gi.
        name (str): The name of the instance type. Example: e2-standard-4.
    """

    cpu: int
    memory: str
    name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cpu = self.cpu

        memory = self.memory

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cpu": cpu,
                "memory": memory,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cpu = d.pop("cpu")

        memory = d.pop("memory")

        name = d.pop("name")

        provider_instance_type = cls(
            cpu=cpu,
            memory=memory,
            name=name,
        )

        provider_instance_type.additional_properties = d
        return provider_instance_type

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
