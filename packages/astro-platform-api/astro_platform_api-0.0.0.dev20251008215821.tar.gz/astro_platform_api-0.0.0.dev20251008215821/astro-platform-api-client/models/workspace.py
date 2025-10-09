import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.basic_subject_profile import BasicSubjectProfile


T = TypeVar("T", bound="Workspace")


@_attrs_define
class Workspace:
    """
    Attributes:
        cicd_enforced_default (bool): Whether CI/CD deploys are enforced by default. Example: True.
        created_at (datetime.datetime): The time when the Workspace was created in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ` Example: 2023-09-08T12:00:00Z.
        id (str): The Workspace's ID. Example: clm8t5u4q000008jq4qoc3036.
        name (str): The Workspace's name. Example: My Workspace.
        organization_id (str): The ID of the organization to which the workspace belongs. Example:
            clm8t5u4q000008jq4qoc3036.
        updated_at (datetime.datetime): The time when the Workspace was updated in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ` Example: 2023-09-08T13:30:00Z.
        created_by (Union[Unset, BasicSubjectProfile]):
        description (Union[Unset, str]): The Workspace's description. Example: This is a test workspace.
        organization_name (Union[Unset, str]): The name of the Organization to which the Workspace belongs. Example: My
            Organization.
        updated_by (Union[Unset, BasicSubjectProfile]):
    """

    cicd_enforced_default: bool
    created_at: datetime.datetime
    id: str
    name: str
    organization_id: str
    updated_at: datetime.datetime
    created_by: Union[Unset, "BasicSubjectProfile"] = UNSET
    description: Union[Unset, str] = UNSET
    organization_name: Union[Unset, str] = UNSET
    updated_by: Union[Unset, "BasicSubjectProfile"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cicd_enforced_default = self.cicd_enforced_default

        created_at = self.created_at.isoformat()

        id = self.id

        name = self.name

        organization_id = self.organization_id

        updated_at = self.updated_at.isoformat()

        created_by: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.created_by, Unset):
            created_by = self.created_by.to_dict()

        description = self.description

        organization_name = self.organization_name

        updated_by: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.updated_by, Unset):
            updated_by = self.updated_by.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cicdEnforcedDefault": cicd_enforced_default,
                "createdAt": created_at,
                "id": id,
                "name": name,
                "organizationId": organization_id,
                "updatedAt": updated_at,
            }
        )
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if description is not UNSET:
            field_dict["description"] = description
        if organization_name is not UNSET:
            field_dict["organizationName"] = organization_name
        if updated_by is not UNSET:
            field_dict["updatedBy"] = updated_by

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.basic_subject_profile import BasicSubjectProfile

        d = dict(src_dict)
        cicd_enforced_default = d.pop("cicdEnforcedDefault")

        created_at = isoparse(d.pop("createdAt"))

        id = d.pop("id")

        name = d.pop("name")

        organization_id = d.pop("organizationId")

        updated_at = isoparse(d.pop("updatedAt"))

        _created_by = d.pop("createdBy", UNSET)
        created_by: Union[Unset, BasicSubjectProfile]
        if isinstance(_created_by, Unset):
            created_by = UNSET
        else:
            created_by = BasicSubjectProfile.from_dict(_created_by)

        description = d.pop("description", UNSET)

        organization_name = d.pop("organizationName", UNSET)

        _updated_by = d.pop("updatedBy", UNSET)
        updated_by: Union[Unset, BasicSubjectProfile]
        if isinstance(_updated_by, Unset):
            updated_by = UNSET
        else:
            updated_by = BasicSubjectProfile.from_dict(_updated_by)

        workspace = cls(
            cicd_enforced_default=cicd_enforced_default,
            created_at=created_at,
            id=id,
            name=name,
            organization_id=organization_id,
            updated_at=updated_at,
            created_by=created_by,
            description=description,
            organization_name=organization_name,
            updated_by=updated_by,
        )

        workspace.additional_properties = d
        return workspace

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
