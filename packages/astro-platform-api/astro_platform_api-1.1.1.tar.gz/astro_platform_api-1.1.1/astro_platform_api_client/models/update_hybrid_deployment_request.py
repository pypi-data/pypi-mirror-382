from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.update_hybrid_deployment_request_executor import UpdateHybridDeploymentRequestExecutor
from ..models.update_hybrid_deployment_request_type import UpdateHybridDeploymentRequestType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.deployment_environment_variable_request import DeploymentEnvironmentVariableRequest
    from ..models.deployment_instance_spec_request import DeploymentInstanceSpecRequest
    from ..models.hybrid_worker_queue_request import HybridWorkerQueueRequest


T = TypeVar("T", bound="UpdateHybridDeploymentRequest")


@_attrs_define
class UpdateHybridDeploymentRequest:
    """
    Attributes:
        environment_variables (list['DeploymentEnvironmentVariableRequest']): List of environment variables to add to
            the Deployment.
        executor (UpdateHybridDeploymentRequestExecutor): The Deployment's executor type. Example: CELERY.
        is_cicd_enforced (bool): Whether the Deployment requires that all deploys are made through CI/CD. Example: True.
        is_dag_deploy_enabled (bool): Whether the Deployment has DAG deploys enabled. Example: True.
        name (str): The Deployment's name. Example: My deployment.
        scheduler (DeploymentInstanceSpecRequest):
        type_ (UpdateHybridDeploymentRequestType): The type of the Deployment. Example: DEDICATED.
        workspace_id (str): The ID of the Workspace to which the Deployment belongs. Example: clmh7vdf4000008lhhlnk9t6o.
        contact_emails (Union[Unset, list[str]]): A list of contact emails for the Deployment. Example:
            ['user1@company.com'].
        description (Union[Unset, str]): The Deployment's description. Example: My deployment description.
        task_pod_node_pool_id (Union[Unset, str]): The node pool ID for worker Pods. Applies only when `Executor` is
            `KUBERNETES`. Example: clmh87air000008mgfkgrg9fy.
        worker_queues (Union[Unset, list['HybridWorkerQueueRequest']]): The list of worker queues configured for the
            Deployment. Applies only when `Executor` is `CELERY`. All Deployments need at least 1 worker queue called
            `default`.
        workload_identity (Union[Unset, str]): The Deployment's workload identity. Example:
            arn:aws:iam::123456789:role/AirflowS3Logs-clmk2qqia000008mhff3ndjr0.
    """

    environment_variables: list["DeploymentEnvironmentVariableRequest"]
    executor: UpdateHybridDeploymentRequestExecutor
    is_cicd_enforced: bool
    is_dag_deploy_enabled: bool
    name: str
    scheduler: "DeploymentInstanceSpecRequest"
    type_: UpdateHybridDeploymentRequestType
    workspace_id: str
    contact_emails: Union[Unset, list[str]] = UNSET
    description: Union[Unset, str] = UNSET
    task_pod_node_pool_id: Union[Unset, str] = UNSET
    worker_queues: Union[Unset, list["HybridWorkerQueueRequest"]] = UNSET
    workload_identity: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        environment_variables = []
        for environment_variables_item_data in self.environment_variables:
            environment_variables_item = environment_variables_item_data.to_dict()
            environment_variables.append(environment_variables_item)

        executor = self.executor.value

        is_cicd_enforced = self.is_cicd_enforced

        is_dag_deploy_enabled = self.is_dag_deploy_enabled

        name = self.name

        scheduler = self.scheduler.to_dict()

        type_ = self.type_.value

        workspace_id = self.workspace_id

        contact_emails: Union[Unset, list[str]] = UNSET
        if not isinstance(self.contact_emails, Unset):
            contact_emails = self.contact_emails

        description = self.description

        task_pod_node_pool_id = self.task_pod_node_pool_id

        worker_queues: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.worker_queues, Unset):
            worker_queues = []
            for worker_queues_item_data in self.worker_queues:
                worker_queues_item = worker_queues_item_data.to_dict()
                worker_queues.append(worker_queues_item)

        workload_identity = self.workload_identity

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "environmentVariables": environment_variables,
                "executor": executor,
                "isCicdEnforced": is_cicd_enforced,
                "isDagDeployEnabled": is_dag_deploy_enabled,
                "name": name,
                "scheduler": scheduler,
                "type": type_,
                "workspaceId": workspace_id,
            }
        )
        if contact_emails is not UNSET:
            field_dict["contactEmails"] = contact_emails
        if description is not UNSET:
            field_dict["description"] = description
        if task_pod_node_pool_id is not UNSET:
            field_dict["taskPodNodePoolId"] = task_pod_node_pool_id
        if worker_queues is not UNSET:
            field_dict["workerQueues"] = worker_queues
        if workload_identity is not UNSET:
            field_dict["workloadIdentity"] = workload_identity

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.deployment_environment_variable_request import DeploymentEnvironmentVariableRequest
        from ..models.deployment_instance_spec_request import DeploymentInstanceSpecRequest
        from ..models.hybrid_worker_queue_request import HybridWorkerQueueRequest

        d = dict(src_dict)
        environment_variables = []
        _environment_variables = d.pop("environmentVariables")
        for environment_variables_item_data in _environment_variables:
            environment_variables_item = DeploymentEnvironmentVariableRequest.from_dict(environment_variables_item_data)

            environment_variables.append(environment_variables_item)

        executor = UpdateHybridDeploymentRequestExecutor(d.pop("executor"))

        is_cicd_enforced = d.pop("isCicdEnforced")

        is_dag_deploy_enabled = d.pop("isDagDeployEnabled")

        name = d.pop("name")

        scheduler = DeploymentInstanceSpecRequest.from_dict(d.pop("scheduler"))

        type_ = UpdateHybridDeploymentRequestType(d.pop("type"))

        workspace_id = d.pop("workspaceId")

        contact_emails = cast(list[str], d.pop("contactEmails", UNSET))

        description = d.pop("description", UNSET)

        task_pod_node_pool_id = d.pop("taskPodNodePoolId", UNSET)

        worker_queues = []
        _worker_queues = d.pop("workerQueues", UNSET)
        for worker_queues_item_data in _worker_queues or []:
            worker_queues_item = HybridWorkerQueueRequest.from_dict(worker_queues_item_data)

            worker_queues.append(worker_queues_item)

        workload_identity = d.pop("workloadIdentity", UNSET)

        update_hybrid_deployment_request = cls(
            environment_variables=environment_variables,
            executor=executor,
            is_cicd_enforced=is_cicd_enforced,
            is_dag_deploy_enabled=is_dag_deploy_enabled,
            name=name,
            scheduler=scheduler,
            type_=type_,
            workspace_id=workspace_id,
            contact_emails=contact_emails,
            description=description,
            task_pod_node_pool_id=task_pod_node_pool_id,
            worker_queues=worker_queues,
            workload_identity=workload_identity,
        )

        update_hybrid_deployment_request.additional_properties = d
        return update_hybrid_deployment_request

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
