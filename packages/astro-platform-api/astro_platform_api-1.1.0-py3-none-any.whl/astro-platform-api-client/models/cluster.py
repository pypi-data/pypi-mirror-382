import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.cluster_cloud_provider import ClusterCloudProvider
from ..models.cluster_status import ClusterStatus
from ..models.cluster_type import ClusterType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cluster_health_status import ClusterHealthStatus
    from ..models.cluster_k8s_tag import ClusterK8STag
    from ..models.cluster_metadata import ClusterMetadata
    from ..models.node_pool import NodePool


T = TypeVar("T", bound="Cluster")


@_attrs_define
class Cluster:
    """
    Attributes:
        cloud_provider (ClusterCloudProvider): The name of the cluster's cloud provider. Example: AWS.
        created_at (datetime.datetime): The time when the cluster was created in UTC. formatted as `YYYY-MM-
            DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        db_instance_type (str): The type of database instance that is used for the cluster. Example: db.t3.medium.
        id (str): The cluster's ID. Example: clm7k8tgw000008jz97i37y81.
        name (str): The cluster's name. Example: my cluster.
        organization_id (str): The ID of the Organization that the cluster belongs to. Example:
            clm88r8hi000008jwhzxu5crg.
        region (str): The region in which the cluster is created. Example: us-east-1.
        status (ClusterStatus): The status of the cluster. Example: CREATED.
        type_ (ClusterType): The type of the cluster. Example: DEDICATED.
        updated_at (datetime.datetime): The time when the cluster was last updated in UTC. formatted as `YYYY-MM-
            DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        vpc_subnet_range (str): The VPC subnet range. Example: 172.20.0.0/22.
        health_status (Union[Unset, ClusterHealthStatus]):
        is_limited (Union[Unset, bool]): Whether the cluster is limited.
        metadata (Union[Unset, ClusterMetadata]):
        node_pools (Union[Unset, list['NodePool']]): The list of node pools that are created in the cluster.
        pod_subnet_range (Union[Unset, str]): The subnet range for Pods. For GCP clusters only. Example: 172.21.0.0/19.
        provider_account (Union[Unset, str]): The provider account ID. For GCP clusters only. Example: provider-account.
        service_peering_range (Union[Unset, str]): The service peering range. For GCP clusters only. Example:
            172.23.0.0/20.
        service_subnet_range (Union[Unset, str]): The service subnet range. For GCP clusters only. Example:
            172.22.0.0/22.
        tags (Union[Unset, list['ClusterK8STag']]): The Kubernetes tags in the cluster. For AWS Hybrid clusters only.
        tenant_id (Union[Unset, str]): The tenant ID. For Azure clusters only. Example: your-tenant-id.
        workspace_ids (Union[Unset, list[str]]): The list of Workspaces that are authorized to the cluster. Example:
            ['clm88rddl000108jwgeka2div'].
    """

    cloud_provider: ClusterCloudProvider
    created_at: datetime.datetime
    db_instance_type: str
    id: str
    name: str
    organization_id: str
    region: str
    status: ClusterStatus
    type_: ClusterType
    updated_at: datetime.datetime
    vpc_subnet_range: str
    health_status: Union[Unset, "ClusterHealthStatus"] = UNSET
    is_limited: Union[Unset, bool] = UNSET
    metadata: Union[Unset, "ClusterMetadata"] = UNSET
    node_pools: Union[Unset, list["NodePool"]] = UNSET
    pod_subnet_range: Union[Unset, str] = UNSET
    provider_account: Union[Unset, str] = UNSET
    service_peering_range: Union[Unset, str] = UNSET
    service_subnet_range: Union[Unset, str] = UNSET
    tags: Union[Unset, list["ClusterK8STag"]] = UNSET
    tenant_id: Union[Unset, str] = UNSET
    workspace_ids: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cloud_provider = self.cloud_provider.value

        created_at = self.created_at.isoformat()

        db_instance_type = self.db_instance_type

        id = self.id

        name = self.name

        organization_id = self.organization_id

        region = self.region

        status = self.status.value

        type_ = self.type_.value

        updated_at = self.updated_at.isoformat()

        vpc_subnet_range = self.vpc_subnet_range

        health_status: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.health_status, Unset):
            health_status = self.health_status.to_dict()

        is_limited = self.is_limited

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        node_pools: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.node_pools, Unset):
            node_pools = []
            for node_pools_item_data in self.node_pools:
                node_pools_item = node_pools_item_data.to_dict()
                node_pools.append(node_pools_item)

        pod_subnet_range = self.pod_subnet_range

        provider_account = self.provider_account

        service_peering_range = self.service_peering_range

        service_subnet_range = self.service_subnet_range

        tags: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = []
            for tags_item_data in self.tags:
                tags_item = tags_item_data.to_dict()
                tags.append(tags_item)

        tenant_id = self.tenant_id

        workspace_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.workspace_ids, Unset):
            workspace_ids = self.workspace_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cloudProvider": cloud_provider,
                "createdAt": created_at,
                "dbInstanceType": db_instance_type,
                "id": id,
                "name": name,
                "organizationId": organization_id,
                "region": region,
                "status": status,
                "type": type_,
                "updatedAt": updated_at,
                "vpcSubnetRange": vpc_subnet_range,
            }
        )
        if health_status is not UNSET:
            field_dict["healthStatus"] = health_status
        if is_limited is not UNSET:
            field_dict["isLimited"] = is_limited
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if node_pools is not UNSET:
            field_dict["nodePools"] = node_pools
        if pod_subnet_range is not UNSET:
            field_dict["podSubnetRange"] = pod_subnet_range
        if provider_account is not UNSET:
            field_dict["providerAccount"] = provider_account
        if service_peering_range is not UNSET:
            field_dict["servicePeeringRange"] = service_peering_range
        if service_subnet_range is not UNSET:
            field_dict["serviceSubnetRange"] = service_subnet_range
        if tags is not UNSET:
            field_dict["tags"] = tags
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if workspace_ids is not UNSET:
            field_dict["workspaceIds"] = workspace_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cluster_health_status import ClusterHealthStatus
        from ..models.cluster_k8s_tag import ClusterK8STag
        from ..models.cluster_metadata import ClusterMetadata
        from ..models.node_pool import NodePool

        d = dict(src_dict)
        cloud_provider = ClusterCloudProvider(d.pop("cloudProvider"))

        created_at = isoparse(d.pop("createdAt"))

        db_instance_type = d.pop("dbInstanceType")

        id = d.pop("id")

        name = d.pop("name")

        organization_id = d.pop("organizationId")

        region = d.pop("region")

        status = ClusterStatus(d.pop("status"))

        type_ = ClusterType(d.pop("type"))

        updated_at = isoparse(d.pop("updatedAt"))

        vpc_subnet_range = d.pop("vpcSubnetRange")

        _health_status = d.pop("healthStatus", UNSET)
        health_status: Union[Unset, ClusterHealthStatus]
        if isinstance(_health_status, Unset):
            health_status = UNSET
        else:
            health_status = ClusterHealthStatus.from_dict(_health_status)

        is_limited = d.pop("isLimited", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, ClusterMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = ClusterMetadata.from_dict(_metadata)

        node_pools = []
        _node_pools = d.pop("nodePools", UNSET)
        for node_pools_item_data in _node_pools or []:
            node_pools_item = NodePool.from_dict(node_pools_item_data)

            node_pools.append(node_pools_item)

        pod_subnet_range = d.pop("podSubnetRange", UNSET)

        provider_account = d.pop("providerAccount", UNSET)

        service_peering_range = d.pop("servicePeeringRange", UNSET)

        service_subnet_range = d.pop("serviceSubnetRange", UNSET)

        tags = []
        _tags = d.pop("tags", UNSET)
        for tags_item_data in _tags or []:
            tags_item = ClusterK8STag.from_dict(tags_item_data)

            tags.append(tags_item)

        tenant_id = d.pop("tenantId", UNSET)

        workspace_ids = cast(list[str], d.pop("workspaceIds", UNSET))

        cluster = cls(
            cloud_provider=cloud_provider,
            created_at=created_at,
            db_instance_type=db_instance_type,
            id=id,
            name=name,
            organization_id=organization_id,
            region=region,
            status=status,
            type_=type_,
            updated_at=updated_at,
            vpc_subnet_range=vpc_subnet_range,
            health_status=health_status,
            is_limited=is_limited,
            metadata=metadata,
            node_pools=node_pools,
            pod_subnet_range=pod_subnet_range,
            provider_account=provider_account,
            service_peering_range=service_peering_range,
            service_subnet_range=service_subnet_range,
            tags=tags,
            tenant_id=tenant_id,
            workspace_ids=workspace_ids,
        )

        cluster.additional_properties = d
        return cluster

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
