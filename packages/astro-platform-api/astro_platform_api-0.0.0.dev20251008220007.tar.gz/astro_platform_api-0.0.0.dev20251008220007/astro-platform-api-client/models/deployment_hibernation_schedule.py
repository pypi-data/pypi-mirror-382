from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeploymentHibernationSchedule")


@_attrs_define
class DeploymentHibernationSchedule:
    """
    Attributes:
        hibernate_at_cron (str): A 5-part cron expression defining the times at which the deployment should hibernate
        is_enabled (bool): Toggle this schedule on or off. If set to false, this schedule will have no effect on
            hibernation.
        wake_at_cron (str): A 5-part cron expression definingh the times at which the deployment should wake from
            hibernation
        description (Union[Unset, str]): A brief description of the schedule
    """

    hibernate_at_cron: str
    is_enabled: bool
    wake_at_cron: str
    description: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        hibernate_at_cron = self.hibernate_at_cron

        is_enabled = self.is_enabled

        wake_at_cron = self.wake_at_cron

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "hibernateAtCron": hibernate_at_cron,
                "isEnabled": is_enabled,
                "wakeAtCron": wake_at_cron,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        hibernate_at_cron = d.pop("hibernateAtCron")

        is_enabled = d.pop("isEnabled")

        wake_at_cron = d.pop("wakeAtCron")

        description = d.pop("description", UNSET)

        deployment_hibernation_schedule = cls(
            hibernate_at_cron=hibernate_at_cron,
            is_enabled=is_enabled,
            wake_at_cron=wake_at_cron,
            description=description,
        )

        deployment_hibernation_schedule.additional_properties = d
        return deployment_hibernation_schedule

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
