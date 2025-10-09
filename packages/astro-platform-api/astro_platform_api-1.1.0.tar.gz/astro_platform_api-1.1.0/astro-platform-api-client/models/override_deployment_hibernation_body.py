import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="OverrideDeploymentHibernationBody")


@_attrs_define
class OverrideDeploymentHibernationBody:
    """
    Attributes:
        is_hibernating (bool): The type of override to perform. Set this value to 'true' to have the Deployment
            hibernate regardless of its hibernation schedule. Set the value to 'false' to have the Deployment wake up
            regardless of its hibernation schedule. Use 'OverrideUntil' to define the length of the override.
        override_until (Union[Unset, datetime.datetime]): The end of the override time in UTC, formatted as 'YYYY-MM-
            DDTHH:MM:SSZ'. If this value isn't specified, the override persists until you end it through the Astro UI or
            another API call.
    """

    is_hibernating: bool
    override_until: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_hibernating = self.is_hibernating

        override_until: Union[Unset, str] = UNSET
        if not isinstance(self.override_until, Unset):
            override_until = self.override_until.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "isHibernating": is_hibernating,
            }
        )
        if override_until is not UNSET:
            field_dict["overrideUntil"] = override_until

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_hibernating = d.pop("isHibernating")

        _override_until = d.pop("overrideUntil", UNSET)
        override_until: Union[Unset, datetime.datetime]
        if isinstance(_override_until, Unset):
            override_until = UNSET
        else:
            override_until = isoparse(_override_until)

        override_deployment_hibernation_body = cls(
            is_hibernating=is_hibernating,
            override_until=override_until,
        )

        override_deployment_hibernation_body.additional_properties = d
        return override_deployment_hibernation_body

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
