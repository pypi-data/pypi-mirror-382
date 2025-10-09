from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConnectionAuthTypeParameter")


@_attrs_define
class ConnectionAuthTypeParameter:
    """
    Attributes:
        airflow_param_name (str): The name of the parameter in Airflow
        data_type (str): The data type of the parameter
        description (str): A description of the parameter
        friendly_name (str): The UI-friendly name for the parameter
        is_in_extra (bool): Whether or not the parameter is included in the "extra" field
        is_required (bool): Whether the parameter is required
        is_secret (bool): Whether the parameter is a secret
        example (Union[Unset, str]): An example value for the parameter
        pattern (Union[Unset, str]): A regex pattern for the parameter
    """

    airflow_param_name: str
    data_type: str
    description: str
    friendly_name: str
    is_in_extra: bool
    is_required: bool
    is_secret: bool
    example: Union[Unset, str] = UNSET
    pattern: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        airflow_param_name = self.airflow_param_name

        data_type = self.data_type

        description = self.description

        friendly_name = self.friendly_name

        is_in_extra = self.is_in_extra

        is_required = self.is_required

        is_secret = self.is_secret

        example = self.example

        pattern = self.pattern

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "airflowParamName": airflow_param_name,
                "dataType": data_type,
                "description": description,
                "friendlyName": friendly_name,
                "isInExtra": is_in_extra,
                "isRequired": is_required,
                "isSecret": is_secret,
            }
        )
        if example is not UNSET:
            field_dict["example"] = example
        if pattern is not UNSET:
            field_dict["pattern"] = pattern

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        airflow_param_name = d.pop("airflowParamName")

        data_type = d.pop("dataType")

        description = d.pop("description")

        friendly_name = d.pop("friendlyName")

        is_in_extra = d.pop("isInExtra")

        is_required = d.pop("isRequired")

        is_secret = d.pop("isSecret")

        example = d.pop("example", UNSET)

        pattern = d.pop("pattern", UNSET)

        connection_auth_type_parameter = cls(
            airflow_param_name=airflow_param_name,
            data_type=data_type,
            description=description,
            friendly_name=friendly_name,
            is_in_extra=is_in_extra,
            is_required=is_required,
            is_secret=is_secret,
            example=example,
            pattern=pattern,
        )

        connection_auth_type_parameter.additional_properties = d
        return connection_auth_type_parameter

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
