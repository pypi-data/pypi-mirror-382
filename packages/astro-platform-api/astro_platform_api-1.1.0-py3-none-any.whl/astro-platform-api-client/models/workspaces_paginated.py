from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.workspace import Workspace


T = TypeVar("T", bound="WorkspacesPaginated")


@_attrs_define
class WorkspacesPaginated:
    """
    Attributes:
        limit (int): The maximum number of workspaces that can be retrieved per page.
        offset (int): The offset for the current page of workspaces in the complete result.
        total_count (int): The total number of Workspaces in the paginated result.
        workspaces (list['Workspace']): An array of Workspace objects representing a list of workspaces.
    """

    limit: int
    offset: int
    total_count: int
    workspaces: list["Workspace"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        limit = self.limit

        offset = self.offset

        total_count = self.total_count

        workspaces = []
        for workspaces_item_data in self.workspaces:
            workspaces_item = workspaces_item_data.to_dict()
            workspaces.append(workspaces_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "limit": limit,
                "offset": offset,
                "totalCount": total_count,
                "workspaces": workspaces,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.workspace import Workspace

        d = dict(src_dict)
        limit = d.pop("limit")

        offset = d.pop("offset")

        total_count = d.pop("totalCount")

        workspaces = []
        _workspaces = d.pop("workspaces")
        for workspaces_item_data in _workspaces:
            workspaces_item = Workspace.from_dict(workspaces_item_data)

            workspaces.append(workspaces_item)

        workspaces_paginated = cls(
            limit=limit,
            offset=offset,
            total_count=total_count,
            workspaces=workspaces,
        )

        workspaces_paginated.additional_properties = d
        return workspaces_paginated

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
