from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.update_dedicated_cluster_request_cluster_type import UpdateDedicatedClusterRequestClusterType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cluster_k8s_tag import ClusterK8STag
    from ..models.update_node_pool_request import UpdateNodePoolRequest


T = TypeVar("T", bound="UpdateDedicatedClusterRequest")


@_attrs_define
class UpdateDedicatedClusterRequest:
    """
    Attributes:
        k_8_s_tags (list['ClusterK8STag']): A list of Kubernetes tags to add to the cluster.
        name (str): The cluster's name. Example: My cluster.
        cluster_type (Union[Unset, UpdateDedicatedClusterRequestClusterType]): The cluster's type. Example: DEDICATED.
        db_instance_type (Union[Unset, str]): The cluster's database instance type. Required for Hybrid clusters.
            Example: Small General Purpose.
        node_pools (Union[Unset, list['UpdateNodePoolRequest']]): A list of node pools to add to the cluster. For Hybrid
            clusters only.
        workspace_ids (Union[Unset, list[str]]): The list of Workspaces that are authorized to the cluster. If this
            value is not provided, the existing list of Workspaces remains. If this value is '[]' then all workspace cluster
            mappings are removed.
    """

    k_8_s_tags: list["ClusterK8STag"]
    name: str
    cluster_type: Union[Unset, UpdateDedicatedClusterRequestClusterType] = UNSET
    db_instance_type: Union[Unset, str] = UNSET
    node_pools: Union[Unset, list["UpdateNodePoolRequest"]] = UNSET
    workspace_ids: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        k_8_s_tags = []
        for k_8_s_tags_item_data in self.k_8_s_tags:
            k_8_s_tags_item = k_8_s_tags_item_data.to_dict()
            k_8_s_tags.append(k_8_s_tags_item)

        name = self.name

        cluster_type: Union[Unset, str] = UNSET
        if not isinstance(self.cluster_type, Unset):
            cluster_type = self.cluster_type.value

        db_instance_type = self.db_instance_type

        node_pools: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.node_pools, Unset):
            node_pools = []
            for node_pools_item_data in self.node_pools:
                node_pools_item = node_pools_item_data.to_dict()
                node_pools.append(node_pools_item)

        workspace_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.workspace_ids, Unset):
            workspace_ids = self.workspace_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "k8sTags": k_8_s_tags,
                "name": name,
            }
        )
        if cluster_type is not UNSET:
            field_dict["clusterType"] = cluster_type
        if db_instance_type is not UNSET:
            field_dict["dbInstanceType"] = db_instance_type
        if node_pools is not UNSET:
            field_dict["nodePools"] = node_pools
        if workspace_ids is not UNSET:
            field_dict["workspaceIds"] = workspace_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cluster_k8s_tag import ClusterK8STag
        from ..models.update_node_pool_request import UpdateNodePoolRequest

        d = dict(src_dict)
        k_8_s_tags = []
        _k_8_s_tags = d.pop("k8sTags")
        for k_8_s_tags_item_data in _k_8_s_tags:
            k_8_s_tags_item = ClusterK8STag.from_dict(k_8_s_tags_item_data)

            k_8_s_tags.append(k_8_s_tags_item)

        name = d.pop("name")

        _cluster_type = d.pop("clusterType", UNSET)
        cluster_type: Union[Unset, UpdateDedicatedClusterRequestClusterType]
        if isinstance(_cluster_type, Unset):
            cluster_type = UNSET
        else:
            cluster_type = UpdateDedicatedClusterRequestClusterType(_cluster_type)

        db_instance_type = d.pop("dbInstanceType", UNSET)

        node_pools = []
        _node_pools = d.pop("nodePools", UNSET)
        for node_pools_item_data in _node_pools or []:
            node_pools_item = UpdateNodePoolRequest.from_dict(node_pools_item_data)

            node_pools.append(node_pools_item)

        workspace_ids = cast(list[str], d.pop("workspaceIds", UNSET))

        update_dedicated_cluster_request = cls(
            k_8_s_tags=k_8_s_tags,
            name=name,
            cluster_type=cluster_type,
            db_instance_type=db_instance_type,
            node_pools=node_pools,
            workspace_ids=workspace_ids,
        )

        update_dedicated_cluster_request.additional_properties = d
        return update_dedicated_cluster_request

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
