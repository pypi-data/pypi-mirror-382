from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.cluster import Cluster


T = TypeVar("T", bound="ClustersPaginated")


@_attrs_define
class ClustersPaginated:
    """
    Attributes:
        clusters (list['Cluster']): The list of clusters in the current page.
        limit (int): The maximum number of clusters in one page. Example: 10.
        offset (int): The offset of the current page of clusters.
        total_count (int): The total number of clusters. Example: 100.
    """

    clusters: list["Cluster"]
    limit: int
    offset: int
    total_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        clusters = []
        for clusters_item_data in self.clusters:
            clusters_item = clusters_item_data.to_dict()
            clusters.append(clusters_item)

        limit = self.limit

        offset = self.offset

        total_count = self.total_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "clusters": clusters,
                "limit": limit,
                "offset": offset,
                "totalCount": total_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cluster import Cluster

        d = dict(src_dict)
        clusters = []
        _clusters = d.pop("clusters")
        for clusters_item_data in _clusters:
            clusters_item = Cluster.from_dict(clusters_item_data)

            clusters.append(clusters_item)

        limit = d.pop("limit")

        offset = d.pop("offset")

        total_count = d.pop("totalCount")

        clusters_paginated = cls(
            clusters=clusters,
            limit=limit,
            offset=offset,
            total_count=total_count,
        )

        clusters_paginated.additional_properties = d
        return clusters_paginated

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
