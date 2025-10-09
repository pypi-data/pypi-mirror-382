from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.update_dag_trigger_notification_channel_request_type import UpdateDagTriggerNotificationChannelRequestType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dag_trigger_notification_channel_definition import DagTriggerNotificationChannelDefinition


T = TypeVar("T", bound="UpdateDagTriggerNotificationChannelRequest")


@_attrs_define
class UpdateDagTriggerNotificationChannelRequest:
    """
    Attributes:
        definition (Union[Unset, DagTriggerNotificationChannelDefinition]):
        is_shared (Union[Unset, bool]): When entity type is scoped to ORGANIZATION or WORKSPACE, this determines if
            child entities can access this notification channel.
        name (Union[Unset, str]): The notification channel's name.
        type_ (Union[Unset, UpdateDagTriggerNotificationChannelRequestType]): The notification channel's type.
    """

    definition: Union[Unset, "DagTriggerNotificationChannelDefinition"] = UNSET
    is_shared: Union[Unset, bool] = UNSET
    name: Union[Unset, str] = UNSET
    type_: Union[Unset, UpdateDagTriggerNotificationChannelRequestType] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        definition: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.definition, Unset):
            definition = self.definition.to_dict()

        is_shared = self.is_shared

        name = self.name

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if definition is not UNSET:
            field_dict["definition"] = definition
        if is_shared is not UNSET:
            field_dict["isShared"] = is_shared
        if name is not UNSET:
            field_dict["name"] = name
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dag_trigger_notification_channel_definition import DagTriggerNotificationChannelDefinition

        d = dict(src_dict)
        _definition = d.pop("definition", UNSET)
        definition: Union[Unset, DagTriggerNotificationChannelDefinition]
        if isinstance(_definition, Unset):
            definition = UNSET
        else:
            definition = DagTriggerNotificationChannelDefinition.from_dict(_definition)

        is_shared = d.pop("isShared", UNSET)

        name = d.pop("name", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, UpdateDagTriggerNotificationChannelRequestType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = UpdateDagTriggerNotificationChannelRequestType(_type_)

        update_dag_trigger_notification_channel_request = cls(
            definition=definition,
            is_shared=is_shared,
            name=name,
            type_=type_,
        )

        update_dag_trigger_notification_channel_request.additional_properties = d
        return update_dag_trigger_notification_channel_request

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
