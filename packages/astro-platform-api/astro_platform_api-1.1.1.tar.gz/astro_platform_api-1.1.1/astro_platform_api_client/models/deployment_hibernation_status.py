from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.deployment_hibernation_status_next_event_type import DeploymentHibernationStatusNextEventType
from ..types import UNSET, Unset

T = TypeVar("T", bound="DeploymentHibernationStatus")


@_attrs_define
class DeploymentHibernationStatus:
    """
    Attributes:
        is_hibernating (bool): If the deployment is currently in hibernating state or not
        next_event_at (Union[Unset, str]): Timestamp of the next scheduled hibernation event for the deployment
        next_event_type (Union[Unset, DeploymentHibernationStatusNextEventType]): The type of the next scheduled event
            for the deployment. Either HIBERNATE or WAKE
        reason (Union[Unset, str]): Reason for the current hibernation state of the deployment
    """

    is_hibernating: bool
    next_event_at: Union[Unset, str] = UNSET
    next_event_type: Union[Unset, DeploymentHibernationStatusNextEventType] = UNSET
    reason: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_hibernating = self.is_hibernating

        next_event_at = self.next_event_at

        next_event_type: Union[Unset, str] = UNSET
        if not isinstance(self.next_event_type, Unset):
            next_event_type = self.next_event_type.value

        reason = self.reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "isHibernating": is_hibernating,
            }
        )
        if next_event_at is not UNSET:
            field_dict["nextEventAt"] = next_event_at
        if next_event_type is not UNSET:
            field_dict["nextEventType"] = next_event_type
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_hibernating = d.pop("isHibernating")

        next_event_at = d.pop("nextEventAt", UNSET)

        _next_event_type = d.pop("nextEventType", UNSET)
        next_event_type: Union[Unset, DeploymentHibernationStatusNextEventType]
        if isinstance(_next_event_type, Unset):
            next_event_type = UNSET
        else:
            next_event_type = DeploymentHibernationStatusNextEventType(_next_event_type)

        reason = d.pop("reason", UNSET)

        deployment_hibernation_status = cls(
            is_hibernating=is_hibernating,
            next_event_at=next_event_at,
            next_event_type=next_event_type,
            reason=reason,
        )

        deployment_hibernation_status.additional_properties = d
        return deployment_hibernation_status

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
