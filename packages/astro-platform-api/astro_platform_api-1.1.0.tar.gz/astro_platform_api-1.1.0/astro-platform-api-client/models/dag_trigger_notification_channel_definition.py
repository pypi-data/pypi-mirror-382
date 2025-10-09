from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DagTriggerNotificationChannelDefinition")


@_attrs_define
class DagTriggerNotificationChannelDefinition:
    """
    Attributes:
        dag_id (str): The DAG ID.
        deployment_api_token (str): The Deployment API token.
        deployment_id (str): The DAG's deployment ID.
    """

    dag_id: str
    deployment_api_token: str
    deployment_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dag_id = self.dag_id

        deployment_api_token = self.deployment_api_token

        deployment_id = self.deployment_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dagId": dag_id,
                "deploymentApiToken": deployment_api_token,
                "deploymentId": deployment_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        dag_id = d.pop("dagId")

        deployment_api_token = d.pop("deploymentApiToken")

        deployment_id = d.pop("deploymentId")

        dag_trigger_notification_channel_definition = cls(
            dag_id=dag_id,
            deployment_api_token=deployment_api_token,
            deployment_id=deployment_id,
        )

        dag_trigger_notification_channel_definition.additional_properties = d
        return dag_trigger_notification_channel_definition

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
