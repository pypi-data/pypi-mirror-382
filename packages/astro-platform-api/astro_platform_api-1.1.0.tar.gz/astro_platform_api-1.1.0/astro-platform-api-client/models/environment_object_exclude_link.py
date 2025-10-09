from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.environment_object_exclude_link_scope import EnvironmentObjectExcludeLinkScope

T = TypeVar("T", bound="EnvironmentObjectExcludeLink")


@_attrs_define
class EnvironmentObjectExcludeLink:
    """
    Attributes:
        scope (EnvironmentObjectExcludeLinkScope): Scope of the excluded entity for environment object
        scope_entity_id (str): ID for the excluded entity for the environment object
    """

    scope: EnvironmentObjectExcludeLinkScope
    scope_entity_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        scope = self.scope.value

        scope_entity_id = self.scope_entity_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "scope": scope,
                "scopeEntityId": scope_entity_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        scope = EnvironmentObjectExcludeLinkScope(d.pop("scope"))

        scope_entity_id = d.pop("scopeEntityId")

        environment_object_exclude_link = cls(
            scope=scope,
            scope_entity_id=scope_entity_id,
        )

        environment_object_exclude_link.additional_properties = d
        return environment_object_exclude_link

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
