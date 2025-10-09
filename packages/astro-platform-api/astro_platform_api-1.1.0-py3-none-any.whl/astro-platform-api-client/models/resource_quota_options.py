from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.resource_option import ResourceOption


T = TypeVar("T", bound="ResourceQuotaOptions")


@_attrs_define
class ResourceQuotaOptions:
    """
    Attributes:
        default_pod_size (ResourceOption):
        resource_quota (ResourceOption):
    """

    default_pod_size: "ResourceOption"
    resource_quota: "ResourceOption"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        default_pod_size = self.default_pod_size.to_dict()

        resource_quota = self.resource_quota.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "defaultPodSize": default_pod_size,
                "resourceQuota": resource_quota,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.resource_option import ResourceOption

        d = dict(src_dict)
        default_pod_size = ResourceOption.from_dict(d.pop("defaultPodSize"))

        resource_quota = ResourceOption.from_dict(d.pop("resourceQuota"))

        resource_quota_options = cls(
            default_pod_size=default_pod_size,
            resource_quota=resource_quota,
        )

        resource_quota_options.additional_properties = d
        return resource_quota_options

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
