from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Bundle")


@_attrs_define
class Bundle:
    """
    Attributes:
        bundle_type (str): The type of bundle.
        deploy_id (str): The ID of the deploy that included the bundle.
        mount_path (str): The path where the Astro mounts the bundle on the Airflow component pods.
        current_version (Union[Unset, str]): The current bundle version.
        desired_version (Union[Unset, str]): The desired version of the bundle.
    """

    bundle_type: str
    deploy_id: str
    mount_path: str
    current_version: Union[Unset, str] = UNSET
    desired_version: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bundle_type = self.bundle_type

        deploy_id = self.deploy_id

        mount_path = self.mount_path

        current_version = self.current_version

        desired_version = self.desired_version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "bundleType": bundle_type,
                "deployId": deploy_id,
                "mountPath": mount_path,
            }
        )
        if current_version is not UNSET:
            field_dict["currentVersion"] = current_version
        if desired_version is not UNSET:
            field_dict["desiredVersion"] = desired_version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bundle_type = d.pop("bundleType")

        deploy_id = d.pop("deployId")

        mount_path = d.pop("mountPath")

        current_version = d.pop("currentVersion", UNSET)

        desired_version = d.pop("desiredVersion", UNSET)

        bundle = cls(
            bundle_type=bundle_type,
            deploy_id=deploy_id,
            mount_path=mount_path,
            current_version=current_version,
            desired_version=desired_version,
        )

        bundle.additional_properties = d
        return bundle

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
