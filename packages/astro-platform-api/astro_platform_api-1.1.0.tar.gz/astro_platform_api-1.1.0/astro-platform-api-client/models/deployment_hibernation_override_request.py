from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeploymentHibernationOverrideRequest")


@_attrs_define
class DeploymentHibernationOverrideRequest:
    """
    Attributes:
        is_hibernating (Union[Unset, bool]): Whether to go into hibernation or not via the override rule
        override_until (Union[Unset, str]): Timestamp till the override on the hibernation schedule is in effect
    """

    is_hibernating: Union[Unset, bool] = UNSET
    override_until: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_hibernating = self.is_hibernating

        override_until = self.override_until

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if is_hibernating is not UNSET:
            field_dict["isHibernating"] = is_hibernating
        if override_until is not UNSET:
            field_dict["overrideUntil"] = override_until

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_hibernating = d.pop("isHibernating", UNSET)

        override_until = d.pop("overrideUntil", UNSET)

        deployment_hibernation_override_request = cls(
            is_hibernating=is_hibernating,
            override_until=override_until,
        )

        deployment_hibernation_override_request.additional_properties = d
        return deployment_hibernation_override_request

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
