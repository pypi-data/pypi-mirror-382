import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.organization_payment_method import OrganizationPaymentMethod
from ..models.organization_product import OrganizationProduct
from ..models.organization_status import OrganizationStatus
from ..models.organization_support_plan import OrganizationSupportPlan
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.basic_subject_profile import BasicSubjectProfile
    from ..models.managed_domain import ManagedDomain
    from ..models.organization_product_plan import OrganizationProductPlan


T = TypeVar("T", bound="Organization")


@_attrs_define
class Organization:
    """
    Attributes:
        allow_enhanced_support_access (bool): Whether the organization allows CRE to have view access to their entities
        created_at (datetime.datetime): The time when the Organization was created in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        created_by (BasicSubjectProfile):
        id (str): The Organization's ID. Example: clmaxoarx000008l2c5ayb9pt.
        is_scim_enabled (bool): Whether SCIM is enabled for the Organization.
        name (str): The Organization's name. Example: My organization.
        support_plan (OrganizationSupportPlan): The Organization's support plan. Example: BUSINESS_CRITICAL.
        updated_at (datetime.datetime): The time when the Organization was last updated in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        updated_by (BasicSubjectProfile):
        billing_email (Union[Unset, str]): The Organization's billing email. Example: billing@company.com.
        managed_domains (Union[Unset, list['ManagedDomain']]): The list of managed domains configured in the
            Organization.
        payment_method (Union[Unset, OrganizationPaymentMethod]): The Organization's payment method. Example:
            CREDIT_CARD.
        product (Union[Unset, OrganizationProduct]): The Organization's product type. Example: HOSTED.
        product_plans (Union[Unset, list['OrganizationProductPlan']]):
        status (Union[Unset, OrganizationStatus]): The Organization's status. Example: ACTIVE.
        trial_expires_at (Union[Unset, datetime.datetime]): The time when the Organization's trial expires in UTC,
            formatted as `YYYY-MM-DDTHH:MM:SSZ`. Organizations that are no longer in Trial will not have a expiry date.
            Example: 2022-11-22T04:37:12Z.
    """

    allow_enhanced_support_access: bool
    created_at: datetime.datetime
    created_by: "BasicSubjectProfile"
    id: str
    is_scim_enabled: bool
    name: str
    support_plan: OrganizationSupportPlan
    updated_at: datetime.datetime
    updated_by: "BasicSubjectProfile"
    billing_email: Union[Unset, str] = UNSET
    managed_domains: Union[Unset, list["ManagedDomain"]] = UNSET
    payment_method: Union[Unset, OrganizationPaymentMethod] = UNSET
    product: Union[Unset, OrganizationProduct] = UNSET
    product_plans: Union[Unset, list["OrganizationProductPlan"]] = UNSET
    status: Union[Unset, OrganizationStatus] = UNSET
    trial_expires_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        allow_enhanced_support_access = self.allow_enhanced_support_access

        created_at = self.created_at.isoformat()

        created_by = self.created_by.to_dict()

        id = self.id

        is_scim_enabled = self.is_scim_enabled

        name = self.name

        support_plan = self.support_plan.value

        updated_at = self.updated_at.isoformat()

        updated_by = self.updated_by.to_dict()

        billing_email = self.billing_email

        managed_domains: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.managed_domains, Unset):
            managed_domains = []
            for managed_domains_item_data in self.managed_domains:
                managed_domains_item = managed_domains_item_data.to_dict()
                managed_domains.append(managed_domains_item)

        payment_method: Union[Unset, str] = UNSET
        if not isinstance(self.payment_method, Unset):
            payment_method = self.payment_method.value

        product: Union[Unset, str] = UNSET
        if not isinstance(self.product, Unset):
            product = self.product.value

        product_plans: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.product_plans, Unset):
            product_plans = []
            for product_plans_item_data in self.product_plans:
                product_plans_item = product_plans_item_data.to_dict()
                product_plans.append(product_plans_item)

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        trial_expires_at: Union[Unset, str] = UNSET
        if not isinstance(self.trial_expires_at, Unset):
            trial_expires_at = self.trial_expires_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "allowEnhancedSupportAccess": allow_enhanced_support_access,
                "createdAt": created_at,
                "createdBy": created_by,
                "id": id,
                "isScimEnabled": is_scim_enabled,
                "name": name,
                "supportPlan": support_plan,
                "updatedAt": updated_at,
                "updatedBy": updated_by,
            }
        )
        if billing_email is not UNSET:
            field_dict["billingEmail"] = billing_email
        if managed_domains is not UNSET:
            field_dict["managedDomains"] = managed_domains
        if payment_method is not UNSET:
            field_dict["paymentMethod"] = payment_method
        if product is not UNSET:
            field_dict["product"] = product
        if product_plans is not UNSET:
            field_dict["productPlans"] = product_plans
        if status is not UNSET:
            field_dict["status"] = status
        if trial_expires_at is not UNSET:
            field_dict["trialExpiresAt"] = trial_expires_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.basic_subject_profile import BasicSubjectProfile
        from ..models.managed_domain import ManagedDomain
        from ..models.organization_product_plan import OrganizationProductPlan

        d = dict(src_dict)
        allow_enhanced_support_access = d.pop("allowEnhancedSupportAccess")

        created_at = isoparse(d.pop("createdAt"))

        created_by = BasicSubjectProfile.from_dict(d.pop("createdBy"))

        id = d.pop("id")

        is_scim_enabled = d.pop("isScimEnabled")

        name = d.pop("name")

        support_plan = OrganizationSupportPlan(d.pop("supportPlan"))

        updated_at = isoparse(d.pop("updatedAt"))

        updated_by = BasicSubjectProfile.from_dict(d.pop("updatedBy"))

        billing_email = d.pop("billingEmail", UNSET)

        managed_domains = []
        _managed_domains = d.pop("managedDomains", UNSET)
        for managed_domains_item_data in _managed_domains or []:
            managed_domains_item = ManagedDomain.from_dict(managed_domains_item_data)

            managed_domains.append(managed_domains_item)

        _payment_method = d.pop("paymentMethod", UNSET)
        payment_method: Union[Unset, OrganizationPaymentMethod]
        if isinstance(_payment_method, Unset):
            payment_method = UNSET
        else:
            payment_method = OrganizationPaymentMethod(_payment_method)

        _product = d.pop("product", UNSET)
        product: Union[Unset, OrganizationProduct]
        if isinstance(_product, Unset):
            product = UNSET
        else:
            product = OrganizationProduct(_product)

        product_plans = []
        _product_plans = d.pop("productPlans", UNSET)
        for product_plans_item_data in _product_plans or []:
            product_plans_item = OrganizationProductPlan.from_dict(product_plans_item_data)

            product_plans.append(product_plans_item)

        _status = d.pop("status", UNSET)
        status: Union[Unset, OrganizationStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = OrganizationStatus(_status)

        _trial_expires_at = d.pop("trialExpiresAt", UNSET)
        trial_expires_at: Union[Unset, datetime.datetime]
        if isinstance(_trial_expires_at, Unset):
            trial_expires_at = UNSET
        else:
            trial_expires_at = isoparse(_trial_expires_at)

        organization = cls(
            allow_enhanced_support_access=allow_enhanced_support_access,
            created_at=created_at,
            created_by=created_by,
            id=id,
            is_scim_enabled=is_scim_enabled,
            name=name,
            support_plan=support_plan,
            updated_at=updated_at,
            updated_by=updated_by,
            billing_email=billing_email,
            managed_domains=managed_domains,
            payment_method=payment_method,
            product=product,
            product_plans=product_plans,
            status=status,
            trial_expires_at=trial_expires_at,
        )

        organization.additional_properties = d
        return organization

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
