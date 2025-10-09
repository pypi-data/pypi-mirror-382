from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cluster_health_status_value import ClusterHealthStatusValue
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cluster_health_status_detail import ClusterHealthStatusDetail


T = TypeVar("T", bound="ClusterHealthStatus")


@_attrs_define
class ClusterHealthStatus:
    """
    Attributes:
        value (ClusterHealthStatusValue): Overall health state (HEALTHY or UNHEALTHY). Example: HEALTHY.
        details (Union[Unset, list['ClusterHealthStatusDetail']]): List of details supporting health assessment.
    """

    value: ClusterHealthStatusValue
    details: Union[Unset, list["ClusterHealthStatusDetail"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = self.value.value

        details: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.details, Unset):
            details = []
            for details_item_data in self.details:
                details_item = details_item_data.to_dict()
                details.append(details_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "value": value,
            }
        )
        if details is not UNSET:
            field_dict["details"] = details

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cluster_health_status_detail import ClusterHealthStatusDetail

        d = dict(src_dict)
        value = ClusterHealthStatusValue(d.pop("value"))

        details = []
        _details = d.pop("details", UNSET)
        for details_item_data in _details or []:
            details_item = ClusterHealthStatusDetail.from_dict(details_item_data)

            details.append(details_item)

        cluster_health_status = cls(
            value=value,
            details=details,
        )

        cluster_health_status.additional_properties = d
        return cluster_health_status

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
