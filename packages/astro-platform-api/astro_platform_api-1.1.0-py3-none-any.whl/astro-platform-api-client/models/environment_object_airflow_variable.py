from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="EnvironmentObjectAirflowVariable")


@_attrs_define
class EnvironmentObjectAirflowVariable:
    """
    Attributes:
        is_secret (bool): Whether the value is a secret or not
        value (str): The value of the Airflow variable. If the value is a secret, the value returned is empty
    """

    is_secret: bool
    value: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_secret = self.is_secret

        value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "isSecret": is_secret,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_secret = d.pop("isSecret")

        value = d.pop("value")

        environment_object_airflow_variable = cls(
            is_secret=is_secret,
            value=value,
        )

        environment_object_airflow_variable.additional_properties = d
        return environment_object_airflow_variable

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
