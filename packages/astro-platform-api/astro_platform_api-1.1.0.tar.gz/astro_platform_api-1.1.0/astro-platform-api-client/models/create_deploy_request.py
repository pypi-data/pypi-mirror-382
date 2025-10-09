from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_deploy_request_type import CreateDeployRequestType
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateDeployRequest")


@_attrs_define
class CreateDeployRequest:
    """
    Attributes:
        type_ (CreateDeployRequestType): The type of deploy. Example: IMAGE_AND_DAG.
        bundle_mount_path (Union[Unset, str]): The path where Astro mounts the bundle on the Airflow component pods.
            Required if deploy type is BUNDLE.
        bundle_type (Union[Unset, str]): The type of bundle deployed. Required if deploy type is BUNDLE. Example: dbt.
        description (Union[Unset, str]): The deploy's description. Example: My deploy description.
    """

    type_: CreateDeployRequestType
    bundle_mount_path: Union[Unset, str] = UNSET
    bundle_type: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        bundle_mount_path = self.bundle_mount_path

        bundle_type = self.bundle_type

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
            }
        )
        if bundle_mount_path is not UNSET:
            field_dict["bundleMountPath"] = bundle_mount_path
        if bundle_type is not UNSET:
            field_dict["bundleType"] = bundle_type
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = CreateDeployRequestType(d.pop("type"))

        bundle_mount_path = d.pop("bundleMountPath", UNSET)

        bundle_type = d.pop("bundleType", UNSET)

        description = d.pop("description", UNSET)

        create_deploy_request = cls(
            type_=type_,
            bundle_mount_path=bundle_mount_path,
            bundle_type=bundle_type,
            description=description,
        )

        create_deploy_request.additional_properties = d
        return create_deploy_request

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
