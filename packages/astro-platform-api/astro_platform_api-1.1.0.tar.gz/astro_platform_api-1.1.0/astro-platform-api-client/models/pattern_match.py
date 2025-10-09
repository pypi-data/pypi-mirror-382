from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.pattern_match_entity_type import PatternMatchEntityType
from ..models.pattern_match_operator_type import PatternMatchOperatorType

T = TypeVar("T", bound="PatternMatch")


@_attrs_define
class PatternMatch:
    """
    Attributes:
        entity_type (PatternMatchEntityType): The type of entity to match against.
        operator_type (PatternMatchOperatorType): The type of operator to use for the pattern match.
        values (list[str]): The values to match against.
    """

    entity_type: PatternMatchEntityType
    operator_type: PatternMatchOperatorType
    values: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        entity_type = self.entity_type.value

        operator_type = self.operator_type.value

        values = self.values

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entityType": entity_type,
                "operatorType": operator_type,
                "values": values,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        entity_type = PatternMatchEntityType(d.pop("entityType"))

        operator_type = PatternMatchOperatorType(d.pop("operatorType"))

        values = cast(list[str], d.pop("values"))

        pattern_match = cls(
            entity_type=entity_type,
            operator_type=operator_type,
            values=values,
        )

        pattern_match.additional_properties = d
        return pattern_match

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
