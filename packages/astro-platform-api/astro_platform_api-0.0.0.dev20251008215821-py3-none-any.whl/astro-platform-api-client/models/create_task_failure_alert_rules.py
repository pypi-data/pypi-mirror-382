from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.create_task_failure_alert_properties import CreateTaskFailureAlertProperties
    from ..models.pattern_match_request import PatternMatchRequest


T = TypeVar("T", bound="CreateTaskFailureAlertRules")


@_attrs_define
class CreateTaskFailureAlertRules:
    """
    Attributes:
        pattern_matches (list['PatternMatchRequest']): The alert's pattern matches to match against.
        properties (CreateTaskFailureAlertProperties):
    """

    pattern_matches: list["PatternMatchRequest"]
    properties: "CreateTaskFailureAlertProperties"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pattern_matches = []
        for pattern_matches_item_data in self.pattern_matches:
            pattern_matches_item = pattern_matches_item_data.to_dict()
            pattern_matches.append(pattern_matches_item)

        properties = self.properties.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "patternMatches": pattern_matches,
                "properties": properties,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_task_failure_alert_properties import CreateTaskFailureAlertProperties
        from ..models.pattern_match_request import PatternMatchRequest

        d = dict(src_dict)
        pattern_matches = []
        _pattern_matches = d.pop("patternMatches")
        for pattern_matches_item_data in _pattern_matches:
            pattern_matches_item = PatternMatchRequest.from_dict(pattern_matches_item_data)

            pattern_matches.append(pattern_matches_item)

        properties = CreateTaskFailureAlertProperties.from_dict(d.pop("properties"))

        create_task_failure_alert_rules = cls(
            pattern_matches=pattern_matches,
            properties=properties,
        )

        create_task_failure_alert_rules.additional_properties = d
        return create_task_failure_alert_rules

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
