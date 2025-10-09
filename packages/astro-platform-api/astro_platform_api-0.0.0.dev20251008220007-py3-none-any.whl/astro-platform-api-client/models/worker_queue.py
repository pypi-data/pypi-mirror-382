from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkerQueue")


@_attrs_define
class WorkerQueue:
    """
    Attributes:
        id (str): The worker queue's ID. Example: clmh9vsuf000908midngba9mw.
        is_default (bool): Whether the worker queue is the default worker queue in the Deployment. Example: True.
        max_worker_count (int): The maximum number of workers that can run at once. Example: 10.
        min_worker_count (int): The minimum number of workers running at once. Example: 1.
        name (str): The worker queue's name. Example: default.
        pod_cpu (str): The maximum number of CPU units available for a worker node. Units are in number of CPU cores.
            Example: 1.
        pod_memory (str): The maximum amount of memory available for a worker node. Units are in Gibibytes or `Gi`.
            Example: 2Gi.
        worker_concurrency (int): The maximum number of concurrent tasks that a worker Pod can run at a time. Example:
            20.
        astro_machine (Union[Unset, str]): The Astro machine size for each worker node in the queue. For Astro Hosted
            only. Example: A5.
        node_pool_id (Union[Unset, str]): The node pool ID associated with the worker queue. Example:
            clmh9yjcn000a08mi8dsgbno9.
    """

    id: str
    is_default: bool
    max_worker_count: int
    min_worker_count: int
    name: str
    pod_cpu: str
    pod_memory: str
    worker_concurrency: int
    astro_machine: Union[Unset, str] = UNSET
    node_pool_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        is_default = self.is_default

        max_worker_count = self.max_worker_count

        min_worker_count = self.min_worker_count

        name = self.name

        pod_cpu = self.pod_cpu

        pod_memory = self.pod_memory

        worker_concurrency = self.worker_concurrency

        astro_machine = self.astro_machine

        node_pool_id = self.node_pool_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "isDefault": is_default,
                "maxWorkerCount": max_worker_count,
                "minWorkerCount": min_worker_count,
                "name": name,
                "podCpu": pod_cpu,
                "podMemory": pod_memory,
                "workerConcurrency": worker_concurrency,
            }
        )
        if astro_machine is not UNSET:
            field_dict["astroMachine"] = astro_machine
        if node_pool_id is not UNSET:
            field_dict["nodePoolId"] = node_pool_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        is_default = d.pop("isDefault")

        max_worker_count = d.pop("maxWorkerCount")

        min_worker_count = d.pop("minWorkerCount")

        name = d.pop("name")

        pod_cpu = d.pop("podCpu")

        pod_memory = d.pop("podMemory")

        worker_concurrency = d.pop("workerConcurrency")

        astro_machine = d.pop("astroMachine", UNSET)

        node_pool_id = d.pop("nodePoolId", UNSET)

        worker_queue = cls(
            id=id,
            is_default=is_default,
            max_worker_count=max_worker_count,
            min_worker_count=min_worker_count,
            name=name,
            pod_cpu=pod_cpu,
            pod_memory=pod_memory,
            worker_concurrency=worker_concurrency,
            astro_machine=astro_machine,
            node_pool_id=node_pool_id,
        )

        worker_queue.additional_properties = d
        return worker_queue

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
