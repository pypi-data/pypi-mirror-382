from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.worker_machine_name import WorkerMachineName

if TYPE_CHECKING:
    from ..models.machine_spec import MachineSpec
    from ..models.range_ import Range


T = TypeVar("T", bound="WorkerMachine")


@_attrs_define
class WorkerMachine:
    """
    Attributes:
        concurrency (Range):
        name (WorkerMachineName): The machine's name.
        spec (MachineSpec):
    """

    concurrency: "Range"
    name: WorkerMachineName
    spec: "MachineSpec"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        concurrency = self.concurrency.to_dict()

        name = self.name.value

        spec = self.spec.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "concurrency": concurrency,
                "name": name,
                "spec": spec,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.machine_spec import MachineSpec
        from ..models.range_ import Range

        d = dict(src_dict)
        concurrency = Range.from_dict(d.pop("concurrency"))

        name = WorkerMachineName(d.pop("name"))

        spec = MachineSpec.from_dict(d.pop("spec"))

        worker_machine = cls(
            concurrency=concurrency,
            name=name,
            spec=spec,
        )

        worker_machine.additional_properties = d
        return worker_machine

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
