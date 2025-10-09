from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MachineSpec")


@_attrs_define
class MachineSpec:
    """
    Attributes:
        cpu (str): The CPU quantity. Units are in number of CPU cores. Example: 1.
        memory (str): The memory quantity. Units in Gibibytes or `Gi`. Example: 2Gi.
        concurrency (Union[Unset, float]): The maximum number of tasks that a given machine instance can run at once.
            Example: 10.
        ephemeral_storage (Union[Unset, str]): The ephemeral storage quantity. Units in Gibibytes or `Gi`. Example:
            10Gi.
    """

    cpu: str
    memory: str
    concurrency: Union[Unset, float] = UNSET
    ephemeral_storage: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cpu = self.cpu

        memory = self.memory

        concurrency = self.concurrency

        ephemeral_storage = self.ephemeral_storage

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cpu": cpu,
                "memory": memory,
            }
        )
        if concurrency is not UNSET:
            field_dict["concurrency"] = concurrency
        if ephemeral_storage is not UNSET:
            field_dict["ephemeralStorage"] = ephemeral_storage

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cpu = d.pop("cpu")

        memory = d.pop("memory")

        concurrency = d.pop("concurrency", UNSET)

        ephemeral_storage = d.pop("ephemeralStorage", UNSET)

        machine_spec = cls(
            cpu=cpu,
            memory=memory,
            concurrency=concurrency,
            ephemeral_storage=ephemeral_storage,
        )

        machine_spec.additional_properties = d
        return machine_spec

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
