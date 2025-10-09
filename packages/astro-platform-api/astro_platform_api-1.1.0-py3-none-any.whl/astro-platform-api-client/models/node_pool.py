import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.node_pool_cloud_provider import NodePoolCloudProvider
from ..types import UNSET, Unset

T = TypeVar("T", bound="NodePool")


@_attrs_define
class NodePool:
    """
    Attributes:
        cloud_provider (NodePoolCloudProvider): The name of the cloud provider. Example: AWS.
        cluster_id (str): The ID of the cluster that the node pool belongs to. Example: clm891jb6000308jrc3vjdtde.
        created_at (datetime.datetime): The time when the node pool was created in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        id (str): The node pool's ID. Example: clm890zhe000208jr39dd0ubs.
        is_default (bool): Whether the node pool is the default node pool of the cluster. Example: True.
        max_node_count (int): The maximum number of nodes that can be created in the node pool. Example: 1.
        name (str): The name of the node pool. Example: default.
        node_instance_type (str): The type of node instance that is used for the node pool. Example: t3.medium.
        updated_at (datetime.datetime): The time when the node pool was last updated in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        supported_astro_machines (Union[Unset, list[str]]): The list of supported Astro machines for the node pool.
            Returned only for Hosted dedicated clusters. Example: ['A5', 'A10'].
    """

    cloud_provider: NodePoolCloudProvider
    cluster_id: str
    created_at: datetime.datetime
    id: str
    is_default: bool
    max_node_count: int
    name: str
    node_instance_type: str
    updated_at: datetime.datetime
    supported_astro_machines: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cloud_provider = self.cloud_provider.value

        cluster_id = self.cluster_id

        created_at = self.created_at.isoformat()

        id = self.id

        is_default = self.is_default

        max_node_count = self.max_node_count

        name = self.name

        node_instance_type = self.node_instance_type

        updated_at = self.updated_at.isoformat()

        supported_astro_machines: Union[Unset, list[str]] = UNSET
        if not isinstance(self.supported_astro_machines, Unset):
            supported_astro_machines = self.supported_astro_machines

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cloudProvider": cloud_provider,
                "clusterId": cluster_id,
                "createdAt": created_at,
                "id": id,
                "isDefault": is_default,
                "maxNodeCount": max_node_count,
                "name": name,
                "nodeInstanceType": node_instance_type,
                "updatedAt": updated_at,
            }
        )
        if supported_astro_machines is not UNSET:
            field_dict["supportedAstroMachines"] = supported_astro_machines

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cloud_provider = NodePoolCloudProvider(d.pop("cloudProvider"))

        cluster_id = d.pop("clusterId")

        created_at = isoparse(d.pop("createdAt"))

        id = d.pop("id")

        is_default = d.pop("isDefault")

        max_node_count = d.pop("maxNodeCount")

        name = d.pop("name")

        node_instance_type = d.pop("nodeInstanceType")

        updated_at = isoparse(d.pop("updatedAt"))

        supported_astro_machines = cast(list[str], d.pop("supportedAstroMachines", UNSET))

        node_pool = cls(
            cloud_provider=cloud_provider,
            cluster_id=cluster_id,
            created_at=created_at,
            id=id,
            is_default=is_default,
            max_node_count=max_node_count,
            name=name,
            node_instance_type=node_instance_type,
            updated_at=updated_at,
            supported_astro_machines=supported_astro_machines,
        )

        node_pool.additional_properties = d
        return node_pool

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
