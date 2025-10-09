from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_environment_object_link_request_scope import CreateEnvironmentObjectLinkRequestScope
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_environment_object_overrides_request import CreateEnvironmentObjectOverridesRequest


T = TypeVar("T", bound="CreateEnvironmentObjectLinkRequest")


@_attrs_define
class CreateEnvironmentObjectLinkRequest:
    """
    Attributes:
        scope (CreateEnvironmentObjectLinkRequestScope): Scope to link the environment object
        scope_entity_id (str): Entity ID of the scope to link the environment object
        overrides (Union[Unset, CreateEnvironmentObjectOverridesRequest]):
    """

    scope: CreateEnvironmentObjectLinkRequestScope
    scope_entity_id: str
    overrides: Union[Unset, "CreateEnvironmentObjectOverridesRequest"] = UNSET
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
        from ..models.create_environment_object_overrides_request import CreateEnvironmentObjectOverridesRequest

        d = dict(src_dict)
        scope = CreateEnvironmentObjectLinkRequestScope(d.pop("scope"))

        scope_entity_id = d.pop("scopeEntityId")

        _overrides = d.pop("overrides", UNSET)
        overrides: Union[Unset, CreateEnvironmentObjectOverridesRequest]
        if isinstance(_overrides, Unset):
            overrides = UNSET
        else:
            overrides = CreateEnvironmentObjectOverridesRequest.from_dict(_overrides)

        create_environment_object_link_request = cls(
            scope=scope,
            scope_entity_id=scope_entity_id,
            overrides=overrides,
        )

        create_environment_object_link_request.additional_properties = d
        return create_environment_object_link_request

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
