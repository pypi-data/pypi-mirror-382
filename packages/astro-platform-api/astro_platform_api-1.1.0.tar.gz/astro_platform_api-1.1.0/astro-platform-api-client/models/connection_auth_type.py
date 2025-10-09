from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.connection_auth_type_parameter import ConnectionAuthTypeParameter


T = TypeVar("T", bound="ConnectionAuthType")


@_attrs_define
class ConnectionAuthType:
    """
    Attributes:
        airflow_type (str): The type of connection in Airflow
        auth_method_name (str): The name of the auth method used in the connection
        description (str): A description of the connection auth type
        id (str): The ID of the connection auth type
        name (str): The name of the connection auth type
        parameters (list['ConnectionAuthTypeParameter']): The parameters for the connection auth type
        provider_package_name (str): The name of the provider package
        guide_path (Union[Unset, str]): The URL to the guide for the connection auth type
        provider_logo (Union[Unset, str]): The URL of the provider logo
    """

    airflow_type: str
    auth_method_name: str
    description: str
    id: str
    name: str
    parameters: list["ConnectionAuthTypeParameter"]
    provider_package_name: str
    guide_path: Union[Unset, str] = UNSET
    provider_logo: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        airflow_type = self.airflow_type

        auth_method_name = self.auth_method_name

        description = self.description

        id = self.id

        name = self.name

        parameters = []
        for parameters_item_data in self.parameters:
            parameters_item = parameters_item_data.to_dict()
            parameters.append(parameters_item)

        provider_package_name = self.provider_package_name

        guide_path = self.guide_path

        provider_logo = self.provider_logo

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "airflowType": airflow_type,
                "authMethodName": auth_method_name,
                "description": description,
                "id": id,
                "name": name,
                "parameters": parameters,
                "providerPackageName": provider_package_name,
            }
        )
        if guide_path is not UNSET:
            field_dict["guidePath"] = guide_path
        if provider_logo is not UNSET:
            field_dict["providerLogo"] = provider_logo

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.connection_auth_type_parameter import ConnectionAuthTypeParameter

        d = dict(src_dict)
        airflow_type = d.pop("airflowType")

        auth_method_name = d.pop("authMethodName")

        description = d.pop("description")

        id = d.pop("id")

        name = d.pop("name")

        parameters = []
        _parameters = d.pop("parameters")
        for parameters_item_data in _parameters:
            parameters_item = ConnectionAuthTypeParameter.from_dict(parameters_item_data)

            parameters.append(parameters_item)

        provider_package_name = d.pop("providerPackageName")

        guide_path = d.pop("guidePath", UNSET)

        provider_logo = d.pop("providerLogo", UNSET)

        connection_auth_type = cls(
            airflow_type=airflow_type,
            auth_method_name=auth_method_name,
            description=description,
            id=id,
            name=name,
            parameters=parameters,
            provider_package_name=provider_package_name,
            guide_path=guide_path,
            provider_logo=provider_logo,
        )

        connection_auth_type.additional_properties = d
        return connection_auth_type

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
