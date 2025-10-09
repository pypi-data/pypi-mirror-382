from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateDagTimelinessAlertProperties")


@_attrs_define
class UpdateDagTimelinessAlertProperties:
    """
    Attributes:
        dag_deadline (Union[Unset, str]): The deadline for the DAG in HH:MM 24-hour format, in UTC time.
        days_of_week (Union[Unset, list[str]]): The days of the week for the alert.
        look_back_period_seconds (Union[Unset, int]): The look-back period in seconds.
    """

    dag_deadline: Union[Unset, str] = UNSET
    days_of_week: Union[Unset, list[str]] = UNSET
    look_back_period_seconds: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dag_deadline = self.dag_deadline

        days_of_week: Union[Unset, list[str]] = UNSET
        if not isinstance(self.days_of_week, Unset):
            days_of_week = self.days_of_week

        look_back_period_seconds = self.look_back_period_seconds

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dag_deadline is not UNSET:
            field_dict["dagDeadline"] = dag_deadline
        if days_of_week is not UNSET:
            field_dict["daysOfWeek"] = days_of_week
        if look_back_period_seconds is not UNSET:
            field_dict["lookBackPeriodSeconds"] = look_back_period_seconds

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        dag_deadline = d.pop("dagDeadline", UNSET)

        days_of_week = cast(list[str], d.pop("daysOfWeek", UNSET))

        look_back_period_seconds = d.pop("lookBackPeriodSeconds", UNSET)

        update_dag_timeliness_alert_properties = cls(
            dag_deadline=dag_deadline,
            days_of_week=days_of_week,
            look_back_period_seconds=look_back_period_seconds,
        )

        update_dag_timeliness_alert_properties.additional_properties = d
        return update_dag_timeliness_alert_properties

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
