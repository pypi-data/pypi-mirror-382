from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.update_environment_object_link_request_scope import UpdateEnvironmentObjectLinkRequestScope
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_environment_object_overrides_request import UpdateEnvironmentObjectOverridesRequest


T = TypeVar("T", bound="UpdateEnvironmentObjectLinkRequest")


@_attrs_define
class UpdateEnvironmentObjectLinkRequest:
    """
    Attributes:
        scope (UpdateEnvironmentObjectLinkRequestScope): Scope of the entity to link the environment object
        scope_entity_id (str): Entity ID to link the environment object
        overrides (Union[Unset, UpdateEnvironmentObjectOverridesRequest]):
    """

    scope: UpdateEnvironmentObjectLinkRequestScope
    scope_entity_id: str
    overrides: Union[Unset, "UpdateEnvironmentObjectOverridesRequest"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        scope = self.scope.value

        scope_entity_id = self.scope_entity_id

        overrides: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.overrides, Unset):
            overrides = self.overrides.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "scope": scope,
                "scopeEntityId": scope_entity_id,
            }
        )
        if overrides is not UNSET:
            field_dict["overrides"] = overrides

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_environment_object_overrides_request import UpdateEnvironmentObjectOverridesRequest

        d = dict(src_dict)
        scope = UpdateEnvironmentObjectLinkRequestScope(d.pop("scope"))

        scope_entity_id = d.pop("scopeEntityId")

        _overrides = d.pop("overrides", UNSET)
        overrides: Union[Unset, UpdateEnvironmentObjectOverridesRequest]
        if isinstance(_overrides, Unset):
            overrides = UNSET
        else:
            overrides = UpdateEnvironmentObjectOverridesRequest.from_dict(_overrides)

        update_environment_object_link_request = cls(
            scope=scope,
            scope_entity_id=scope_entity_id,
            overrides=overrides,
        )

        update_environment_object_link_request.additional_properties = d
        return update_environment_object_link_request

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
