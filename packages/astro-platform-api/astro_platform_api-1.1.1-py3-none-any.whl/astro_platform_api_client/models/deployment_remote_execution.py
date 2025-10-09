from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeploymentRemoteExecution")


@_attrs_define
class DeploymentRemoteExecution:
    """
    Attributes:
        allowed_ip_address_ranges (list[str]):
        enabled (bool):
        remote_api_url (str):
        task_log_bucket (Union[Unset, str]):
        task_log_url_pattern (Union[Unset, str]):
    """

    allowed_ip_address_ranges: list[str]
    enabled: bool
    remote_api_url: str
    task_log_bucket: Union[Unset, str] = UNSET
    task_log_url_pattern: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        allowed_ip_address_ranges = self.allowed_ip_address_ranges

        enabled = self.enabled

        remote_api_url = self.remote_api_url

        task_log_bucket = self.task_log_bucket

        task_log_url_pattern = self.task_log_url_pattern

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "allowedIpAddressRanges": allowed_ip_address_ranges,
                "enabled": enabled,
                "remoteApiUrl": remote_api_url,
            }
        )
        if task_log_bucket is not UNSET:
            field_dict["taskLogBucket"] = task_log_bucket
        if task_log_url_pattern is not UNSET:
            field_dict["taskLogUrlPattern"] = task_log_url_pattern

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        allowed_ip_address_ranges = cast(list[str], d.pop("allowedIpAddressRanges"))

        enabled = d.pop("enabled")

        remote_api_url = d.pop("remoteApiUrl")

        task_log_bucket = d.pop("taskLogBucket", UNSET)

        task_log_url_pattern = d.pop("taskLogUrlPattern", UNSET)

        deployment_remote_execution = cls(
            allowed_ip_address_ranges=allowed_ip_address_ranges,
            enabled=enabled,
            remote_api_url=remote_api_url,
            task_log_bucket=task_log_bucket,
            task_log_url_pattern=task_log_url_pattern,
        )

        deployment_remote_execution.additional_properties = d
        return deployment_remote_execution

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
