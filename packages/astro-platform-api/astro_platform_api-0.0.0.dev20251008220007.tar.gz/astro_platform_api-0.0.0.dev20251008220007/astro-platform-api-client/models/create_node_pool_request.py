from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateNodePoolRequest")


@_attrs_define
class CreateNodePoolRequest:
    """
    Attributes:
        max_node_count (int): The maximum number of nodes that can be created in the node pool. Example: 10.
        name (str): The name of the node pool. Example: my-nodepool.
        node_instance_type (str): The type of node instance that is used for the node pool. Example: t3.medium.
        is_default (Union[Unset, bool]): Whether the node pool is the default node pool of the cluster. Example: True.
    """

    max_node_count: int
    name: str
    node_instance_type: str
    is_default: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        max_node_count = self.max_node_count

        name = self.name

        node_instance_type = self.node_instance_type

        is_default = self.is_default

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "maxNodeCount": max_node_count,
                "name": name,
                "nodeInstanceType": node_instance_type,
            }
        )
        if is_default is not UNSET:
            field_dict["isDefault"] = is_default

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        max_node_count = d.pop("maxNodeCount")

        name = d.pop("name")

        node_instance_type = d.pop("nodeInstanceType")

        is_default = d.pop("isDefault", UNSET)

        create_node_pool_request = cls(
            max_node_count=max_node_count,
            name=name,
            node_instance_type=node_instance_type,
            is_default=is_default,
        )

        create_node_pool_request.additional_properties = d
        return create_node_pool_request

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
