from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CreateDagTimelinessAlertProperties")


@_attrs_define
class CreateDagTimelinessAlertProperties:
    """
    Attributes:
        dag_deadline (str): The deadline for the DAG in HH:MM 24-hour format, in UTC time.
        days_of_week (list[str]): The days of the week for the alert.
        deployment_id (str): The ID of the deployment to which the alert is scoped.
        look_back_period_seconds (int): The look-back period in seconds.
    """

    dag_deadline: str
    days_of_week: list[str]
    deployment_id: str
    look_back_period_seconds: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dag_deadline = self.dag_deadline

        days_of_week = self.days_of_week

        deployment_id = self.deployment_id

        look_back_period_seconds = self.look_back_period_seconds

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dagDeadline": dag_deadline,
                "daysOfWeek": days_of_week,
                "deploymentId": deployment_id,
                "lookBackPeriodSeconds": look_back_period_seconds,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        dag_deadline = d.pop("dagDeadline")

        days_of_week = cast(list[str], d.pop("daysOfWeek"))

        deployment_id = d.pop("deploymentId")

        look_back_period_seconds = d.pop("lookBackPeriodSeconds")

        create_dag_timeliness_alert_properties = cls(
            dag_deadline=dag_deadline,
            days_of_week=days_of_week,
            deployment_id=deployment_id,
            look_back_period_seconds=look_back_period_seconds,
        )

        create_dag_timeliness_alert_properties.additional_properties = d
        return create_dag_timeliness_alert_properties

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
