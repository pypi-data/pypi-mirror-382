from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_gcp_cluster_request_cloud_provider import CreateGcpClusterRequestCloudProvider
from ..models.create_gcp_cluster_request_type import CreateGcpClusterRequestType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cluster_k8s_tag import ClusterK8STag
    from ..models.create_node_pool_request import CreateNodePoolRequest


T = TypeVar("T", bound="CreateGcpClusterRequest")


@_attrs_define
class CreateGcpClusterRequest:
    """
    Attributes:
        cloud_provider (CreateGcpClusterRequestCloudProvider): The cluster's cloud provider. Example: AZURE.
        name (str): The cluster's name. Example: My cluster.
        pod_subnet_range (str): The subnet range for Pods. For GCP clusters only. Example: 172.21.0.0/19.
        region (str): The cluster's region. Example: us-east-1.
        service_peering_range (str): The service subnet range. For GCP clusters only. Example: 172.23.0.0/20.
        service_subnet_range (str): The service peering range. For GCP clusters only. Example: 172.22.0.0/22.
        type_ (CreateGcpClusterRequestType): The cluster's type. Example: DEDICATED.
        vpc_subnet_range (str): The VPC subnet range. Example: 172.20.0.0/22.
        db_instance_type (Union[Unset, str]): The type of database instance that is used for the cluster. Required for
            Hybrid clusters. Example: Small General Purpose.
        k_8_s_tags (Union[Unset, list['ClusterK8STag']]): The Kubernetes tags in the cluster.
        node_pools (Union[Unset, list['CreateNodePoolRequest']]): The list of node pools to create in the cluster.
        provider_account (Union[Unset, str]): The provider account ID. Required for Hybrid clusters. Example: provider-
            account.
        workspace_ids (Union[Unset, list[str]]): The list of Workspaces that are authorized to the cluster.
    """

    cloud_provider: CreateGcpClusterRequestCloudProvider
    name: str
    pod_subnet_range: str
    region: str
    service_peering_range: str
    service_subnet_range: str
    type_: CreateGcpClusterRequestType
    vpc_subnet_range: str
    db_instance_type: Union[Unset, str] = UNSET
    k_8_s_tags: Union[Unset, list["ClusterK8STag"]] = UNSET
    node_pools: Union[Unset, list["CreateNodePoolRequest"]] = UNSET
    provider_account: Union[Unset, str] = UNSET
    workspace_ids: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cloud_provider = self.cloud_provider.value

        name = self.name

        pod_subnet_range = self.pod_subnet_range

        region = self.region

        service_peering_range = self.service_peering_range

        service_subnet_range = self.service_subnet_range

        type_ = self.type_.value

        vpc_subnet_range = self.vpc_subnet_range

        db_instance_type = self.db_instance_type

        k_8_s_tags: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.k_8_s_tags, Unset):
            k_8_s_tags = []
            for k_8_s_tags_item_data in self.k_8_s_tags:
                k_8_s_tags_item = k_8_s_tags_item_data.to_dict()
                k_8_s_tags.append(k_8_s_tags_item)

        node_pools: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.node_pools, Unset):
            node_pools = []
            for node_pools_item_data in self.node_pools:
                node_pools_item = node_pools_item_data.to_dict()
                node_pools.append(node_pools_item)

        provider_account = self.provider_account

        workspace_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.workspace_ids, Unset):
            workspace_ids = self.workspace_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cloudProvider": cloud_provider,
                "name": name,
                "podSubnetRange": pod_subnet_range,
                "region": region,
                "servicePeeringRange": service_peering_range,
                "serviceSubnetRange": service_subnet_range,
                "type": type_,
                "vpcSubnetRange": vpc_subnet_range,
            }
        )
        if db_instance_type is not UNSET:
            field_dict["dbInstanceType"] = db_instance_type
        if k_8_s_tags is not UNSET:
            field_dict["k8sTags"] = k_8_s_tags
        if node_pools is not UNSET:
            field_dict["nodePools"] = node_pools
        if provider_account is not UNSET:
            field_dict["providerAccount"] = provider_account
        if workspace_ids is not UNSET:
            field_dict["workspaceIds"] = workspace_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cluster_k8s_tag import ClusterK8STag
        from ..models.create_node_pool_request import CreateNodePoolRequest

        d = dict(src_dict)
        cloud_provider = CreateGcpClusterRequestCloudProvider(d.pop("cloudProvider"))

        name = d.pop("name")

        pod_subnet_range = d.pop("podSubnetRange")

        region = d.pop("region")

        service_peering_range = d.pop("servicePeeringRange")

        service_subnet_range = d.pop("serviceSubnetRange")

        type_ = CreateGcpClusterRequestType(d.pop("type"))

        vpc_subnet_range = d.pop("vpcSubnetRange")

        db_instance_type = d.pop("dbInstanceType", UNSET)

        k_8_s_tags = []
        _k_8_s_tags = d.pop("k8sTags", UNSET)
        for k_8_s_tags_item_data in _k_8_s_tags or []:
            k_8_s_tags_item = ClusterK8STag.from_dict(k_8_s_tags_item_data)

            k_8_s_tags.append(k_8_s_tags_item)

        node_pools = []
        _node_pools = d.pop("nodePools", UNSET)
        for node_pools_item_data in _node_pools or []:
            node_pools_item = CreateNodePoolRequest.from_dict(node_pools_item_data)

            node_pools.append(node_pools_item)

        provider_account = d.pop("providerAccount", UNSET)

        workspace_ids = cast(list[str], d.pop("workspaceIds", UNSET))

        create_gcp_cluster_request = cls(
            cloud_provider=cloud_provider,
            name=name,
            pod_subnet_range=pod_subnet_range,
            region=region,
            service_peering_range=service_peering_range,
            service_subnet_range=service_subnet_range,
            type_=type_,
            vpc_subnet_range=vpc_subnet_range,
            db_instance_type=db_instance_type,
            k_8_s_tags=k_8_s_tags,
            node_pools=node_pools,
            provider_account=provider_account,
            workspace_ids=workspace_ids,
        )

        create_gcp_cluster_request.additional_properties = d
        return create_gcp_cluster_request

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
