from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateEnvironmentObjectAirflowVariableRequest")


@_attrs_define
class CreateEnvironmentObjectAirflowVariableRequest:
    """
    Attributes:
        is_secret (Union[Unset, bool]): Whether the value is a secret or not
        value (Union[Unset, str]): The value of the Airflow variable
    """

    is_secret: Union[Unset, bool] = UNSET
    value: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_secret = self.is_secret

        value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if is_secret is not UNSET:
            field_dict["isSecret"] = is_secret
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_secret = d.pop("isSecret", UNSET)

        value = d.pop("value", UNSET)

        create_environment_object_airflow_variable_request = cls(
            is_secret=is_secret,
            value=value,
        )

        create_environment_object_airflow_variable_request.additional_properties = d
        return create_environment_object_airflow_variable_request

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
