from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_dag_failure_alert_request_entity_type import CreateDagFailureAlertRequestEntityType
from ..models.create_dag_failure_alert_request_severity import CreateDagFailureAlertRequestSeverity
from ..models.create_dag_failure_alert_request_type import CreateDagFailureAlertRequestType

if TYPE_CHECKING:
    from ..models.create_dag_failure_alert_rules import CreateDagFailureAlertRules


T = TypeVar("T", bound="CreateDagFailureAlertRequest")


@_attrs_define
class CreateDagFailureAlertRequest:
    """
    Attributes:
        entity_id (str): The entity ID the alert is associated with.
        entity_type (CreateDagFailureAlertRequestEntityType): The ID of the Deployment to which the alert is scoped.
        name (str): The alert's name.
        notification_channel_ids (list[str]): The notification channels to send alerts to.
        rules (CreateDagFailureAlertRules):
        severity (CreateDagFailureAlertRequestSeverity): The alert's severity.
        type_ (CreateDagFailureAlertRequestType): The alert's type.
    """

    entity_id: str
    entity_type: CreateDagFailureAlertRequestEntityType
    name: str
    notification_channel_ids: list[str]
    rules: "CreateDagFailureAlertRules"
    severity: CreateDagFailureAlertRequestSeverity
    type_: CreateDagFailureAlertRequestType
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        entity_id = self.entity_id

        entity_type = self.entity_type.value

        name = self.name

        notification_channel_ids = self.notification_channel_ids

        rules = self.rules.to_dict()

        severity = self.severity.value

        type_ = self.type_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entityId": entity_id,
                "entityType": entity_type,
                "name": name,
                "notificationChannelIds": notification_channel_ids,
                "rules": rules,
                "severity": severity,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_dag_failure_alert_rules import CreateDagFailureAlertRules

        d = dict(src_dict)
        entity_id = d.pop("entityId")

        entity_type = CreateDagFailureAlertRequestEntityType(d.pop("entityType"))

        name = d.pop("name")

        notification_channel_ids = cast(list[str], d.pop("notificationChannelIds"))

        rules = CreateDagFailureAlertRules.from_dict(d.pop("rules"))

        severity = CreateDagFailureAlertRequestSeverity(d.pop("severity"))

        type_ = CreateDagFailureAlertRequestType(d.pop("type"))

        create_dag_failure_alert_request = cls(
            entity_id=entity_id,
            entity_type=entity_type,
            name=name,
            notification_channel_ids=notification_channel_ids,
            rules=rules,
            severity=severity,
            type_=type_,
        )

        create_dag_failure_alert_request.additional_properties = d
        return create_dag_failure_alert_request

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
