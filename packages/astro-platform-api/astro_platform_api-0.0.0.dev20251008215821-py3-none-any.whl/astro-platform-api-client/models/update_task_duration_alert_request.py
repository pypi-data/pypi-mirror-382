from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.update_task_duration_alert_request_severity import UpdateTaskDurationAlertRequestSeverity
from ..models.update_task_duration_alert_request_type import UpdateTaskDurationAlertRequestType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_task_duration_alert_rules import UpdateTaskDurationAlertRules


T = TypeVar("T", bound="UpdateTaskDurationAlertRequest")


@_attrs_define
class UpdateTaskDurationAlertRequest:
    """
    Attributes:
        name (Union[Unset, str]): The alert's name.
        notification_channel_ids (Union[Unset, list[str]]): The notification channels to send alerts to.
        rules (Union[Unset, UpdateTaskDurationAlertRules]):
        severity (Union[Unset, UpdateTaskDurationAlertRequestSeverity]): The alert's severity.
        type_ (Union[Unset, UpdateTaskDurationAlertRequestType]): The alert's type.
    """

    name: Union[Unset, str] = UNSET
    notification_channel_ids: Union[Unset, list[str]] = UNSET
    rules: Union[Unset, "UpdateTaskDurationAlertRules"] = UNSET
    severity: Union[Unset, UpdateTaskDurationAlertRequestSeverity] = UNSET
    type_: Union[Unset, UpdateTaskDurationAlertRequestType] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        notification_channel_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.notification_channel_ids, Unset):
            notification_channel_ids = self.notification_channel_ids

        rules: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.rules, Unset):
            rules = self.rules.to_dict()

        severity: Union[Unset, str] = UNSET
        if not isinstance(self.severity, Unset):
            severity = self.severity.value

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if notification_channel_ids is not UNSET:
            field_dict["notificationChannelIds"] = notification_channel_ids
        if rules is not UNSET:
            field_dict["rules"] = rules
        if severity is not UNSET:
            field_dict["severity"] = severity
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_task_duration_alert_rules import UpdateTaskDurationAlertRules

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        notification_channel_ids = cast(list[str], d.pop("notificationChannelIds", UNSET))

        _rules = d.pop("rules", UNSET)
        rules: Union[Unset, UpdateTaskDurationAlertRules]
        if isinstance(_rules, Unset):
            rules = UNSET
        else:
            rules = UpdateTaskDurationAlertRules.from_dict(_rules)

        _severity = d.pop("severity", UNSET)
        severity: Union[Unset, UpdateTaskDurationAlertRequestSeverity]
        if isinstance(_severity, Unset):
            severity = UNSET
        else:
            severity = UpdateTaskDurationAlertRequestSeverity(_severity)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, UpdateTaskDurationAlertRequestType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = UpdateTaskDurationAlertRequestType(_type_)

        update_task_duration_alert_request = cls(
            name=name,
            notification_channel_ids=notification_channel_ids,
            rules=rules,
            severity=severity,
            type_=type_,
        )

        update_task_duration_alert_request.additional_properties = d
        return update_task_duration_alert_request

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
