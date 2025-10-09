from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ClusterHealthStatusDetail")


@_attrs_define
class ClusterHealthStatusDetail:
    """
    Attributes:
        code (str): The health status for a specific component.
        description (str): A description of the component that was assessed.
        severity (str): The weight this component is given in overall cluster health assessment.
        component (Union[Unset, str]):
    """

    code: str
    description: str
    severity: str
    component: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        code = self.code

        description = self.description

        severity = self.severity

        component = self.component

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code": code,
                "description": description,
                "severity": severity,
            }
        )
        if component is not UNSET:
            field_dict["component"] = component

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        code = d.pop("code")

        description = d.pop("description")

        severity = d.pop("severity")

        component = d.pop("component", UNSET)

        cluster_health_status_detail = cls(
            code=code,
            description=description,
            severity=severity,
            component=component,
        )

        cluster_health_status_detail.additional_properties = d
        return cluster_health_status_detail

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
