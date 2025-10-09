import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.managed_domain_status import ManagedDomainStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="ManagedDomain")


@_attrs_define
class ManagedDomain:
    """
    Attributes:
        created_at (datetime.datetime): The time when the domain was created in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`.
        id (str): The managed domain's ID. Example: cln203mz7000008jv0jyz9m3y.
        name (str): The managed domain's name/ URL. Example: mycompany.com.
        organization_id (str): The ID of the Organization to which the managed domain belongs. Example:
            cln204xr2000008mu3hhe3zwe.
        status (ManagedDomainStatus): Whether the managed domain has completed the verification process.
        updated_at (datetime.datetime): The time when the domain was last updated in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`.
        enforced_logins (Union[Unset, list[str]]): A list of login types that are enforced for users belonging to the
            domain. Example: ['password'].
    """

    created_at: datetime.datetime
    id: str
    name: str
    organization_id: str
    status: ManagedDomainStatus
    updated_at: datetime.datetime
    enforced_logins: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at.isoformat()

        id = self.id

        name = self.name

        organization_id = self.organization_id

        status = self.status.value

        updated_at = self.updated_at.isoformat()

        enforced_logins: Union[Unset, list[str]] = UNSET
        if not isinstance(self.enforced_logins, Unset):
            enforced_logins = self.enforced_logins

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "createdAt": created_at,
                "id": id,
                "name": name,
                "organizationId": organization_id,
                "status": status,
                "updatedAt": updated_at,
            }
        )
        if enforced_logins is not UNSET:
            field_dict["enforcedLogins"] = enforced_logins

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_at = isoparse(d.pop("createdAt"))

        id = d.pop("id")

        name = d.pop("name")

        organization_id = d.pop("organizationId")

        status = ManagedDomainStatus(d.pop("status"))

        updated_at = isoparse(d.pop("updatedAt"))

        enforced_logins = cast(list[str], d.pop("enforcedLogins", UNSET))

        managed_domain = cls(
            created_at=created_at,
            id=id,
            name=name,
            organization_id=organization_id,
            status=status,
            updated_at=updated_at,
            enforced_logins=enforced_logins,
        )

        managed_domain.additional_properties = d
        return managed_domain

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
