from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FinalizeDeployRequest")


@_attrs_define
class FinalizeDeployRequest:
    """
    Attributes:
        bundle_tarball_version (Union[Unset, str]): The deploy's bundle tarball version. Required if DAG deploy is
            enabled on the Deployment and deploy type is BUNDLE.
        dag_tarball_version (Union[Unset, str]): The deploy's DAG tarball version, also known as the Bundle Version in
            the Astro UI. Required if DAG deploys are enabled on the Deployment, and deploy type is either IMAGE_AND_DAG or
            DAG_ONLY.
    """

    bundle_tarball_version: Union[Unset, str] = UNSET
    dag_tarball_version: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bundle_tarball_version = self.bundle_tarball_version

        dag_tarball_version = self.dag_tarball_version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bundle_tarball_version is not UNSET:
            field_dict["bundleTarballVersion"] = bundle_tarball_version
        if dag_tarball_version is not UNSET:
            field_dict["dagTarballVersion"] = dag_tarball_version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bundle_tarball_version = d.pop("bundleTarballVersion", UNSET)

        dag_tarball_version = d.pop("dagTarballVersion", UNSET)

        finalize_deploy_request = cls(
            bundle_tarball_version=bundle_tarball_version,
            dag_tarball_version=dag_tarball_version,
        )

        finalize_deploy_request.additional_properties = d
        return finalize_deploy_request

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
