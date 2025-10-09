from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="HybridWorkerQueueRequest")


@_attrs_define
class HybridWorkerQueueRequest:
    """
    Attributes:
        is_default (bool): Whether the worker queue is the default worker queue on the Deployment. Example: True.
        max_worker_count (int): The maximum number of workers that can run at once.
        min_worker_count (int): The minimum number of workers running at once.
        name (str): The worker queue's name. Example: My worker queue.
        node_pool_id (str): The node pool ID associated with the worker queue.
        worker_concurrency (int): The maximum number of concurrent tasks that a worker Pod can run at a time.
        id (Union[Unset, str]): The worker queue's ID. If not provided, a new worker queue will be created. Example:
            clmha1mzc000b08mi96n182au.
    """

    is_default: bool
    max_worker_count: int
    min_worker_count: int
    name: str
    node_pool_id: str
    worker_concurrency: int
    id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_default = self.is_default

        max_worker_count = self.max_worker_count

        min_worker_count = self.min_worker_count

        name = self.name

        node_pool_id = self.node_pool_id

        worker_concurrency = self.worker_concurrency

        id = self.id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "isDefault": is_default,
                "maxWorkerCount": max_worker_count,
                "minWorkerCount": min_worker_count,
                "name": name,
                "nodePoolId": node_pool_id,
                "workerConcurrency": worker_concurrency,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_default = d.pop("isDefault")

        max_worker_count = d.pop("maxWorkerCount")

        min_worker_count = d.pop("minWorkerCount")

        name = d.pop("name")

        node_pool_id = d.pop("nodePoolId")

        worker_concurrency = d.pop("workerConcurrency")

        id = d.pop("id", UNSET)

        hybrid_worker_queue_request = cls(
            is_default=is_default,
            max_worker_count=max_worker_count,
            min_worker_count=min_worker_count,
            name=name,
            node_pool_id=node_pool_id,
            worker_concurrency=worker_concurrency,
            id=id,
        )

        hybrid_worker_queue_request.additional_properties = d
        return hybrid_worker_queue_request

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
