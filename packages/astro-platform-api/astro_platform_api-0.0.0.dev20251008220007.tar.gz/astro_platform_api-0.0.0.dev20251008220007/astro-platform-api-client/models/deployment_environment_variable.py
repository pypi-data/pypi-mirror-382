from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeploymentEnvironmentVariable")


@_attrs_define
class DeploymentEnvironmentVariable:
    """
    Attributes:
        is_secret (bool): Whether the environment variable is a secret. Example: True.
        key (str): The environment variable key, used to call the value in code. Example: my-var.
        updated_at (str): The time when the environment variable was last updated in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        value (Union[Unset, str]): The environment variable value. Example: my-var-value.
    """

    is_secret: bool
    key: str
    updated_at: str
    value: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_secret = self.is_secret

        key = self.key

        updated_at = self.updated_at

        value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "isSecret": is_secret,
                "key": key,
                "updatedAt": updated_at,
            }
        )
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_secret = d.pop("isSecret")

        key = d.pop("key")

        updated_at = d.pop("updatedAt")

        value = d.pop("value", UNSET)

        deployment_environment_variable = cls(
            is_secret=is_secret,
            key=key,
            updated_at=updated_at,
            value=value,
        )

        deployment_environment_variable.additional_properties = d
        return deployment_environment_variable

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
