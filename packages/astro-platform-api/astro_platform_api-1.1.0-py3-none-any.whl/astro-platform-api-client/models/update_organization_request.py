from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateOrganizationRequest")


@_attrs_define
class UpdateOrganizationRequest:
    """
    Attributes:
        billing_email (str): The Organization's billing email. Example: billing@company.com.
        is_scim_enabled (bool): Whether SCIM is enabled for the Organization.
        name (str): The name of the Organization. Example: My Organization.
        allow_enhanced_support_access (Union[Unset, bool]):
    """

    billing_email: str
    is_scim_enabled: bool
    name: str
    allow_enhanced_support_access: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        billing_email = self.billing_email

        is_scim_enabled = self.is_scim_enabled

        name = self.name

        allow_enhanced_support_access = self.allow_enhanced_support_access

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "billingEmail": billing_email,
                "isScimEnabled": is_scim_enabled,
                "name": name,
            }
        )
        if allow_enhanced_support_access is not UNSET:
            field_dict["allowEnhancedSupportAccess"] = allow_enhanced_support_access

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        billing_email = d.pop("billingEmail")

        is_scim_enabled = d.pop("isScimEnabled")

        name = d.pop("name")

        allow_enhanced_support_access = d.pop("allowEnhancedSupportAccess", UNSET)

        update_organization_request = cls(
            billing_email=billing_email,
            is_scim_enabled=is_scim_enabled,
            name=name,
            allow_enhanced_support_access=allow_enhanced_support_access,
        )

        update_organization_request.additional_properties = d
        return update_organization_request

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
