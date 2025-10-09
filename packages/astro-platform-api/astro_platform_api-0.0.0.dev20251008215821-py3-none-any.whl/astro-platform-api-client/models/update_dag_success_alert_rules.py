from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pattern_match_request import PatternMatchRequest


T = TypeVar("T", bound="UpdateDagSuccessAlertRules")


@_attrs_define
class UpdateDagSuccessAlertRules:
    """
    Attributes:
        pattern_matches (Union[Unset, list['PatternMatchRequest']]): The alert's pattern matches to match against.
    """

    pattern_matches: Union[Unset, list["PatternMatchRequest"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pattern_matches: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.pattern_matches, Unset):
            pattern_matches = []
            for pattern_matches_item_data in self.pattern_matches:
                pattern_matches_item = pattern_matches_item_data.to_dict()
                pattern_matches.append(pattern_matches_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pattern_matches is not UNSET:
            field_dict["patternMatches"] = pattern_matches

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pattern_match_request import PatternMatchRequest

        d = dict(src_dict)
        pattern_matches = []
        _pattern_matches = d.pop("patternMatches", UNSET)
        for pattern_matches_item_data in _pattern_matches or []:
            pattern_matches_item = PatternMatchRequest.from_dict(pattern_matches_item_data)

            pattern_matches.append(pattern_matches_item)

        update_dag_success_alert_rules = cls(
            pattern_matches=pattern_matches,
        )

        update_dag_success_alert_rules.additional_properties = d
        return update_dag_success_alert_rules

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
