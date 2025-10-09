from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.organization_product_plan_astronomer_product import OrganizationProductPlanAstronomerProduct

T = TypeVar("T", bound="OrganizationProductPlan")


@_attrs_define
class OrganizationProductPlan:
    """
    Attributes:
        astronomer_product (OrganizationProductPlanAstronomerProduct):
        organization_id (str):
        product_plan_id (str):
        product_plan_name (str):
    """

    astronomer_product: OrganizationProductPlanAstronomerProduct
    organization_id: str
    product_plan_id: str
    product_plan_name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        astronomer_product = self.astronomer_product.value

        organization_id = self.organization_id

        product_plan_id = self.product_plan_id

        product_plan_name = self.product_plan_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "astronomerProduct": astronomer_product,
                "organizationId": organization_id,
                "productPlanId": product_plan_id,
                "productPlanName": product_plan_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        astronomer_product = OrganizationProductPlanAstronomerProduct(d.pop("astronomerProduct"))

        organization_id = d.pop("organizationId")

        product_plan_id = d.pop("productPlanId")

        product_plan_name = d.pop("productPlanName")

        organization_product_plan = cls(
            astronomer_product=astronomer_product,
            organization_id=organization_id,
            product_plan_id=product_plan_id,
            product_plan_name=product_plan_name,
        )

        organization_product_plan.additional_properties = d
        return organization_product_plan

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
