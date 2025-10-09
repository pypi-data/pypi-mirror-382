from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cluster_options_provider import ClusterOptionsProvider
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.provider_instance_type import ProviderInstanceType
    from ..models.provider_region import ProviderRegion


T = TypeVar("T", bound="ClusterOptions")


@_attrs_define
class ClusterOptions:
    """
    Attributes:
        database_instances (list['ProviderInstanceType']): The available database instances.
        default_database_instance (ProviderInstanceType):
        default_node_instance (ProviderInstanceType):
        default_region (ProviderRegion):
        default_vpc_subnet_range (str): The default VPC subnet range. Example: 172.20.0.0/19.
        node_count_default (int): The default number of nodes. Example: 20.
        node_count_max (int): The maximum number of nodes. Example: 100.
        node_count_min (int): The minimum number of nodes. Example: 2.
        node_instances (list['ProviderInstanceType']): The available node instances.
        provider (ClusterOptionsProvider): The cloud provider. Example: AZURE.
        regions (list['ProviderRegion']): The available regions.
        default_pod_subnet_range (Union[Unset, str]): The default pod subnet range. Example: 172.21.0.0/19.
        default_service_peering_range (Union[Unset, str]): The default service peering range. Example: 172.23.0.0/20.
        default_service_subnet_range (Union[Unset, str]): The default service subnet range. Example: 172.22.0.0/22.
    """

    database_instances: list["ProviderInstanceType"]
    default_database_instance: "ProviderInstanceType"
    default_node_instance: "ProviderInstanceType"
    default_region: "ProviderRegion"
    default_vpc_subnet_range: str
    node_count_default: int
    node_count_max: int
    node_count_min: int
    node_instances: list["ProviderInstanceType"]
    provider: ClusterOptionsProvider
    regions: list["ProviderRegion"]
    default_pod_subnet_range: Union[Unset, str] = UNSET
    default_service_peering_range: Union[Unset, str] = UNSET
    default_service_subnet_range: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        database_instances = []
        for database_instances_item_data in self.database_instances:
            database_instances_item = database_instances_item_data.to_dict()
            database_instances.append(database_instances_item)

        default_database_instance = self.default_database_instance.to_dict()

        default_node_instance = self.default_node_instance.to_dict()

        default_region = self.default_region.to_dict()

        default_vpc_subnet_range = self.default_vpc_subnet_range

        node_count_default = self.node_count_default

        node_count_max = self.node_count_max

        node_count_min = self.node_count_min

        node_instances = []
        for node_instances_item_data in self.node_instances:
            node_instances_item = node_instances_item_data.to_dict()
            node_instances.append(node_instances_item)

        provider = self.provider.value

        regions = []
        for regions_item_data in self.regions:
            regions_item = regions_item_data.to_dict()
            regions.append(regions_item)

        default_pod_subnet_range = self.default_pod_subnet_range

        default_service_peering_range = self.default_service_peering_range

        default_service_subnet_range = self.default_service_subnet_range

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "databaseInstances": database_instances,
                "defaultDatabaseInstance": default_database_instance,
                "defaultNodeInstance": default_node_instance,
                "defaultRegion": default_region,
                "defaultVpcSubnetRange": default_vpc_subnet_range,
                "nodeCountDefault": node_count_default,
                "nodeCountMax": node_count_max,
                "nodeCountMin": node_count_min,
                "nodeInstances": node_instances,
                "provider": provider,
                "regions": regions,
            }
        )
        if default_pod_subnet_range is not UNSET:
            field_dict["defaultPodSubnetRange"] = default_pod_subnet_range
        if default_service_peering_range is not UNSET:
            field_dict["defaultServicePeeringRange"] = default_service_peering_range
        if default_service_subnet_range is not UNSET:
            field_dict["defaultServiceSubnetRange"] = default_service_subnet_range

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.provider_instance_type import ProviderInstanceType
        from ..models.provider_region import ProviderRegion

        d = dict(src_dict)
        database_instances = []
        _database_instances = d.pop("databaseInstances")
        for database_instances_item_data in _database_instances:
            database_instances_item = ProviderInstanceType.from_dict(database_instances_item_data)

            database_instances.append(database_instances_item)

        default_database_instance = ProviderInstanceType.from_dict(d.pop("defaultDatabaseInstance"))

        default_node_instance = ProviderInstanceType.from_dict(d.pop("defaultNodeInstance"))

        default_region = ProviderRegion.from_dict(d.pop("defaultRegion"))

        default_vpc_subnet_range = d.pop("defaultVpcSubnetRange")

        node_count_default = d.pop("nodeCountDefault")

        node_count_max = d.pop("nodeCountMax")

        node_count_min = d.pop("nodeCountMin")

        node_instances = []
        _node_instances = d.pop("nodeInstances")
        for node_instances_item_data in _node_instances:
            node_instances_item = ProviderInstanceType.from_dict(node_instances_item_data)

            node_instances.append(node_instances_item)

        provider = ClusterOptionsProvider(d.pop("provider"))

        regions = []
        _regions = d.pop("regions")
        for regions_item_data in _regions:
            regions_item = ProviderRegion.from_dict(regions_item_data)

            regions.append(regions_item)

        default_pod_subnet_range = d.pop("defaultPodSubnetRange", UNSET)

        default_service_peering_range = d.pop("defaultServicePeeringRange", UNSET)

        default_service_subnet_range = d.pop("defaultServiceSubnetRange", UNSET)

        cluster_options = cls(
            database_instances=database_instances,
            default_database_instance=default_database_instance,
            default_node_instance=default_node_instance,
            default_region=default_region,
            default_vpc_subnet_range=default_vpc_subnet_range,
            node_count_default=node_count_default,
            node_count_max=node_count_max,
            node_count_min=node_count_min,
            node_instances=node_instances,
            provider=provider,
            regions=regions,
            default_pod_subnet_range=default_pod_subnet_range,
            default_service_peering_range=default_service_peering_range,
            default_service_subnet_range=default_service_subnet_range,
        )

        cluster_options.additional_properties = d
        return cluster_options

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
