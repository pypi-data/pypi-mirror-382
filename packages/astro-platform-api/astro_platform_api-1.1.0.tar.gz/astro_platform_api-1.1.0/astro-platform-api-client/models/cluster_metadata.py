from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ClusterMetadata")


@_attrs_define
class ClusterMetadata:
    """
    Attributes:
        external_i_ps (Union[Unset, list[str]]): External IPs of the cluster. Example: ['35.100.100.1'].
        kube_dns_ip (Union[Unset, str]): The IP address of the kube-dns service. Example: 10.100.100.0.
        oidc_issuer_url (Union[Unset, str]): OIDC issuer URL for the cluster Example: https://westus2.oic.prod-
            aks.azure.com/b84efac8-cfae-467a-b223-23b9aea1486d/3075f79e-abc2-4602-a691-28117197e83d/.
    """

    external_i_ps: Union[Unset, list[str]] = UNSET
    kube_dns_ip: Union[Unset, str] = UNSET
    oidc_issuer_url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        external_i_ps: Union[Unset, list[str]] = UNSET
        if not isinstance(self.external_i_ps, Unset):
            external_i_ps = self.external_i_ps

        kube_dns_ip = self.kube_dns_ip

        oidc_issuer_url = self.oidc_issuer_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if external_i_ps is not UNSET:
            field_dict["externalIPs"] = external_i_ps
        if kube_dns_ip is not UNSET:
            field_dict["kubeDnsIp"] = kube_dns_ip
        if oidc_issuer_url is not UNSET:
            field_dict["oidcIssuerUrl"] = oidc_issuer_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        external_i_ps = cast(list[str], d.pop("externalIPs", UNSET))

        kube_dns_ip = d.pop("kubeDnsIp", UNSET)

        oidc_issuer_url = d.pop("oidcIssuerUrl", UNSET)

        cluster_metadata = cls(
            external_i_ps=external_i_ps,
            kube_dns_ip=kube_dns_ip,
            oidc_issuer_url=oidc_issuer_url,
        )

        cluster_metadata.additional_properties = d
        return cluster_metadata

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
