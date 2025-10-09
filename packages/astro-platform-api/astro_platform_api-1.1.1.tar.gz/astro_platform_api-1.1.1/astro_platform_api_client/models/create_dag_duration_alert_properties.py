from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CreateDagDurationAlertProperties")


@_attrs_define
class CreateDagDurationAlertProperties:
    """
    Attributes:
        dag_duration_seconds (int): The duration of the DAG in seconds.
        deployment_id (str): The ID of the deployment to which the alert is scoped.
    """

    dag_duration_seconds: int
    deployment_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dag_duration_seconds = self.dag_duration_seconds

        deployment_id = self.deployment_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dagDurationSeconds": dag_duration_seconds,
                "deploymentId": deployment_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        dag_duration_seconds = d.pop("dagDurationSeconds")

        deployment_id = d.pop("deploymentId")

        create_dag_duration_alert_properties = cls(
            dag_duration_seconds=dag_duration_seconds,
            deployment_id=deployment_id,
        )

        create_dag_duration_alert_properties.additional_properties = d
        return create_dag_duration_alert_properties

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
