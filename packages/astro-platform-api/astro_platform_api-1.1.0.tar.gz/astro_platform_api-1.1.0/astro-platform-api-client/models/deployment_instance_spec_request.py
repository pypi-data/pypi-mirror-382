from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DeploymentInstanceSpecRequest")


@_attrs_define
class DeploymentInstanceSpecRequest:
    """
    Attributes:
        au (int): The number of Astro unit allocated to the Deployment pod. Minimum `5`, Maximum `24`. Example: 5.
        replicas (int): The number of replicas the pod should have. Minimum `1`, Maximum `4`. Example: 1.
    """

    au: int
    replicas: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        au = self.au

        replicas = self.replicas

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "au": au,
                "replicas": replicas,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        au = d.pop("au")

        replicas = d.pop("replicas")

        deployment_instance_spec_request = cls(
            au=au,
            replicas=replicas,
        )

        deployment_instance_spec_request.additional_properties = d
        return deployment_instance_spec_request

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
