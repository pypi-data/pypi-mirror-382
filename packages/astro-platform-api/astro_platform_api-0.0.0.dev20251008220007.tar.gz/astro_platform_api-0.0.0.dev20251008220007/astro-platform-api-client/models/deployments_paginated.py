from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.deployment import Deployment


T = TypeVar("T", bound="DeploymentsPaginated")


@_attrs_define
class DeploymentsPaginated:
    """
    Attributes:
        deployments (list['Deployment']): A list of Deployments in the current page.
        limit (int): The maximum number of Deployments in one page. Example: 10.
        offset (int): The offset of the current page of Deployments.
        total_count (int): The total number of Deployments. Example: 100.
    """

    deployments: list["Deployment"]
    limit: int
    offset: int
    total_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        deployments = []
        for deployments_item_data in self.deployments:
            deployments_item = deployments_item_data.to_dict()
            deployments.append(deployments_item)

        limit = self.limit

        offset = self.offset

        total_count = self.total_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "deployments": deployments,
                "limit": limit,
                "offset": offset,
                "totalCount": total_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.deployment import Deployment

        d = dict(src_dict)
        deployments = []
        _deployments = d.pop("deployments")
        for deployments_item_data in _deployments:
            deployments_item = Deployment.from_dict(deployments_item_data)

            deployments.append(deployments_item)

        limit = d.pop("limit")

        offset = d.pop("offset")

        total_count = d.pop("totalCount")

        deployments_paginated = cls(
            deployments=deployments,
            limit=limit,
            offset=offset,
            total_count=total_count,
        )

        deployments_paginated.additional_properties = d
        return deployments_paginated

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
