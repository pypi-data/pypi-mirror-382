from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.update_hybrid_cluster_request_cluster_type import UpdateHybridClusterRequestClusterType
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateHybridClusterRequest")


@_attrs_define
class UpdateHybridClusterRequest:
    """
    Attributes:
        cluster_type (UpdateHybridClusterRequestClusterType): The cluster's type. Example: HYBRID.
        workspace_ids (Union[Unset, list[str]]): The list of Workspaces that are authorized to the cluster. If this
            value is not provided, the existing list of Workspaces remains. If this value is '[]' then all workspace cluster
            mappings are removed.
    """

    cluster_type: UpdateHybridClusterRequestClusterType
    workspace_ids: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cluster_type = self.cluster_type.value

        workspace_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.workspace_ids, Unset):
            workspace_ids = self.workspace_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "clusterType": cluster_type,
            }
        )
        if workspace_ids is not UNSET:
            field_dict["workspaceIds"] = workspace_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cluster_type = UpdateHybridClusterRequestClusterType(d.pop("clusterType"))

        workspace_ids = cast(list[str], d.pop("workspaceIds", UNSET))

        update_hybrid_cluster_request = cls(
            cluster_type=cluster_type,
            workspace_ids=workspace_ids,
        )

        update_hybrid_cluster_request.additional_properties = d
        return update_hybrid_cluster_request

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
