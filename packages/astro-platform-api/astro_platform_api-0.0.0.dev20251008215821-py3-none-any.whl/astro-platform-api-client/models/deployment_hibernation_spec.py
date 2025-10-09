from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.deployment_hibernation_override import DeploymentHibernationOverride
    from ..models.deployment_hibernation_schedule import DeploymentHibernationSchedule


T = TypeVar("T", bound="DeploymentHibernationSpec")


@_attrs_define
class DeploymentHibernationSpec:
    """
    Attributes:
        override (Union[Unset, DeploymentHibernationOverride]):
        schedules (Union[Unset, list['DeploymentHibernationSchedule']]): The list of schedules for deployment
            hibernation
    """

    override: Union[Unset, "DeploymentHibernationOverride"] = UNSET
    schedules: Union[Unset, list["DeploymentHibernationSchedule"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        override: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.override, Unset):
            override = self.override.to_dict()

        schedules: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.schedules, Unset):
            schedules = []
            for schedules_item_data in self.schedules:
                schedules_item = schedules_item_data.to_dict()
                schedules.append(schedules_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if override is not UNSET:
            field_dict["override"] = override
        if schedules is not UNSET:
            field_dict["schedules"] = schedules

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.deployment_hibernation_override import DeploymentHibernationOverride
        from ..models.deployment_hibernation_schedule import DeploymentHibernationSchedule

        d = dict(src_dict)
        _override = d.pop("override", UNSET)
        override: Union[Unset, DeploymentHibernationOverride]
        if isinstance(_override, Unset):
            override = UNSET
        else:
            override = DeploymentHibernationOverride.from_dict(_override)

        schedules = []
        _schedules = d.pop("schedules", UNSET)
        for schedules_item_data in _schedules or []:
            schedules_item = DeploymentHibernationSchedule.from_dict(schedules_item_data)

            schedules.append(schedules_item)

        deployment_hibernation_spec = cls(
            override=override,
            schedules=schedules,
        )

        deployment_hibernation_spec.additional_properties = d
        return deployment_hibernation_spec

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
