from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateWorkspaceRequest")


@_attrs_define
class CreateWorkspaceRequest:
    """
    Attributes:
        name (str): The Workspace's name. Example: My Workspace.
        cicd_enforced_default (Union[Unset, bool]): Whether new Deployments enforce CI/CD deploys by default. Example:
            True.
        description (Union[Unset, str]): The Workspace's description. Example: This is a test workspace.
    """

    name: str
    cicd_enforced_default: Union[Unset, bool] = UNSET
    description: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        cicd_enforced_default = self.cicd_enforced_default

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if cicd_enforced_default is not UNSET:
            field_dict["cicdEnforcedDefault"] = cicd_enforced_default
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        cicd_enforced_default = d.pop("cicdEnforcedDefault", UNSET)

        description = d.pop("description", UNSET)

        create_workspace_request = cls(
            name=name,
            cicd_enforced_default=cicd_enforced_default,
            description=description,
        )

        create_workspace_request.additional_properties = d
        return create_workspace_request

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
