from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.update_standard_deployment_request_executor import UpdateStandardDeploymentRequestExecutor
from ..models.update_standard_deployment_request_scheduler_size import UpdateStandardDeploymentRequestSchedulerSize
from ..models.update_standard_deployment_request_type import UpdateStandardDeploymentRequestType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.deployment_environment_variable_request import DeploymentEnvironmentVariableRequest
    from ..models.deployment_remote_execution_request import DeploymentRemoteExecutionRequest
    from ..models.deployment_scaling_spec_request import DeploymentScalingSpecRequest
    from ..models.worker_queue_request import WorkerQueueRequest


T = TypeVar("T", bound="UpdateStandardDeploymentRequest")


@_attrs_define
class UpdateStandardDeploymentRequest:
    """
    Attributes:
        environment_variables (list['DeploymentEnvironmentVariableRequest']): List of environment variables to add to
            the Deployment.
        executor (UpdateStandardDeploymentRequestExecutor): The Deployment's executor type. Example: CELERY.
        is_cicd_enforced (bool): Whether the Deployment requires that all deploys are made through CI/CD. Example: True.
        is_dag_deploy_enabled (bool): Whether the Deployment has DAG deploys enabled. Example: True.
        is_high_availability (bool): Whether the Deployment is configured for high availability. If `true`, multiple
            scheduler pods will be online. Example: True.
        name (str): The Deployment's name. Example: My deployment.
        scheduler_size (UpdateStandardDeploymentRequestSchedulerSize): The size of the scheduler Pod. Example: MEDIUM.
        type_ (UpdateStandardDeploymentRequestType): The type of the Deployment. Example: DEDICATED.
        workspace_id (str): The ID of the Workspace to which the Deployment belongs. Example: clmh7vdf4000008lhhlnk9t6o.
        contact_emails (Union[Unset, list[str]]): A list of contact emails for the Deployment. Example:
            ['user1@company.com'].
        default_task_pod_cpu (Union[Unset, str]): The default CPU resource usage for a worker Pod when running the
            Kubernetes executor or KubernetesPodOperator. Units are in number of CPU cores. Required if Remote Execution is
            disabled. Example: 0.5.
        default_task_pod_memory (Union[Unset, str]): The default memory resource usage for a worker Pod when running the
            Kubernetes executor or KubernetesPodOperator. Units are in `Gi` and must be explicitly included. This value must
            always be twice the value of `DefaultTaskPodCpu`. Required if Remote Execution is disabled. Example: 1Gi.
        description (Union[Unset, str]): The Deployment's description. Example: My deployment description.
        is_development_mode (Union[Unset, bool]): Whether the Deployment is for development only. If `false`, the
            Deployment can be considered production for the purposes of support case priority, but development-only features
            such as hibernation will not be available. You can't update this value to `true` for existing non-development
            Deployments.
        remote_execution (Union[Unset, DeploymentRemoteExecutionRequest]):
        resource_quota_cpu (Union[Unset, str]): The CPU quota for worker Pods when running the Kubernetes executor or
            KubernetesPodOperator. If current CPU usage across all workers exceeds the quota, no new worker Pods can be
            scheduled. Units are in number of CPU cores. Required if Remote Execution is disabled. Example: 160.
        resource_quota_memory (Union[Unset, str]): The memory quota for worker Pods when running the Kubernetes executor
            or KubernetesPodOperator. If current memory usage across all workers exceeds the quota, no new worker Pods can
            be scheduled. Units are in `Gi` and must be explicitly included. This value must always be twice the value of
            `ResourceQuotaCpu`. Required if Remote Execution is disabled. Example: 320Gi.
        scaling_spec (Union[Unset, DeploymentScalingSpecRequest]):
        worker_queues (Union[Unset, list['WorkerQueueRequest']]): A list of the Deployment's worker queues. Applies only
            when `Executor` is `CELERY` or if Remote Execution is disabled and executor is `ASTRO`. All these Deployments
            need at least 1 worker queue called `default`.
        workload_identity (Union[Unset, str]): The Deployment's workload identity. Example:
            arn:aws:iam::123456789:role/AirflowS3Logs-clmk2qqia000008mhff3ndjr0.
    """

    environment_variables: list["DeploymentEnvironmentVariableRequest"]
    executor: UpdateStandardDeploymentRequestExecutor
    is_cicd_enforced: bool
    is_dag_deploy_enabled: bool
    is_high_availability: bool
    name: str
    scheduler_size: UpdateStandardDeploymentRequestSchedulerSize
    type_: UpdateStandardDeploymentRequestType
    workspace_id: str
    contact_emails: Union[Unset, list[str]] = UNSET
    default_task_pod_cpu: Union[Unset, str] = UNSET
    default_task_pod_memory: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    is_development_mode: Union[Unset, bool] = UNSET
    remote_execution: Union[Unset, "DeploymentRemoteExecutionRequest"] = UNSET
    resource_quota_cpu: Union[Unset, str] = UNSET
    resource_quota_memory: Union[Unset, str] = UNSET
    scaling_spec: Union[Unset, "DeploymentScalingSpecRequest"] = UNSET
    worker_queues: Union[Unset, list["WorkerQueueRequest"]] = UNSET
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

        is_high_availability = self.is_high_availability

        name = self.name

        scheduler_size = self.scheduler_size.value

        type_ = self.type_.value

        workspace_id = self.workspace_id

        contact_emails: Union[Unset, list[str]] = UNSET
        if not isinstance(self.contact_emails, Unset):
            contact_emails = self.contact_emails

        default_task_pod_cpu = self.default_task_pod_cpu

        default_task_pod_memory = self.default_task_pod_memory

        description = self.description

        is_development_mode = self.is_development_mode

        remote_execution: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.remote_execution, Unset):
            remote_execution = self.remote_execution.to_dict()

        resource_quota_cpu = self.resource_quota_cpu

        resource_quota_memory = self.resource_quota_memory

        scaling_spec: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.scaling_spec, Unset):
            scaling_spec = self.scaling_spec.to_dict()

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
                "isHighAvailability": is_high_availability,
                "name": name,
                "schedulerSize": scheduler_size,
                "type": type_,
                "workspaceId": workspace_id,
            }
        )
        if contact_emails is not UNSET:
            field_dict["contactEmails"] = contact_emails
        if default_task_pod_cpu is not UNSET:
            field_dict["defaultTaskPodCpu"] = default_task_pod_cpu
        if default_task_pod_memory is not UNSET:
            field_dict["defaultTaskPodMemory"] = default_task_pod_memory
        if description is not UNSET:
            field_dict["description"] = description
        if is_development_mode is not UNSET:
            field_dict["isDevelopmentMode"] = is_development_mode
        if remote_execution is not UNSET:
            field_dict["remoteExecution"] = remote_execution
        if resource_quota_cpu is not UNSET:
            field_dict["resourceQuotaCpu"] = resource_quota_cpu
        if resource_quota_memory is not UNSET:
            field_dict["resourceQuotaMemory"] = resource_quota_memory
        if scaling_spec is not UNSET:
            field_dict["scalingSpec"] = scaling_spec
        if worker_queues is not UNSET:
            field_dict["workerQueues"] = worker_queues
        if workload_identity is not UNSET:
            field_dict["workloadIdentity"] = workload_identity

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.deployment_environment_variable_request import DeploymentEnvironmentVariableRequest
        from ..models.deployment_remote_execution_request import DeploymentRemoteExecutionRequest
        from ..models.deployment_scaling_spec_request import DeploymentScalingSpecRequest
        from ..models.worker_queue_request import WorkerQueueRequest

        d = dict(src_dict)
        environment_variables = []
        _environment_variables = d.pop("environmentVariables")
        for environment_variables_item_data in _environment_variables:
            environment_variables_item = DeploymentEnvironmentVariableRequest.from_dict(environment_variables_item_data)

            environment_variables.append(environment_variables_item)

        executor = UpdateStandardDeploymentRequestExecutor(d.pop("executor"))

        is_cicd_enforced = d.pop("isCicdEnforced")

        is_dag_deploy_enabled = d.pop("isDagDeployEnabled")

        is_high_availability = d.pop("isHighAvailability")

        name = d.pop("name")

        scheduler_size = UpdateStandardDeploymentRequestSchedulerSize(d.pop("schedulerSize"))

        type_ = UpdateStandardDeploymentRequestType(d.pop("type"))

        workspace_id = d.pop("workspaceId")

        contact_emails = cast(list[str], d.pop("contactEmails", UNSET))

        default_task_pod_cpu = d.pop("defaultTaskPodCpu", UNSET)

        default_task_pod_memory = d.pop("defaultTaskPodMemory", UNSET)

        description = d.pop("description", UNSET)

        is_development_mode = d.pop("isDevelopmentMode", UNSET)

        _remote_execution = d.pop("remoteExecution", UNSET)
        remote_execution: Union[Unset, DeploymentRemoteExecutionRequest]
        if isinstance(_remote_execution, Unset):
            remote_execution = UNSET
        else:
            remote_execution = DeploymentRemoteExecutionRequest.from_dict(_remote_execution)

        resource_quota_cpu = d.pop("resourceQuotaCpu", UNSET)

        resource_quota_memory = d.pop("resourceQuotaMemory", UNSET)

        _scaling_spec = d.pop("scalingSpec", UNSET)
        scaling_spec: Union[Unset, DeploymentScalingSpecRequest]
        if isinstance(_scaling_spec, Unset):
            scaling_spec = UNSET
        else:
            scaling_spec = DeploymentScalingSpecRequest.from_dict(_scaling_spec)

        worker_queues = []
        _worker_queues = d.pop("workerQueues", UNSET)
        for worker_queues_item_data in _worker_queues or []:
            worker_queues_item = WorkerQueueRequest.from_dict(worker_queues_item_data)

            worker_queues.append(worker_queues_item)

        workload_identity = d.pop("workloadIdentity", UNSET)

        update_standard_deployment_request = cls(
            environment_variables=environment_variables,
            executor=executor,
            is_cicd_enforced=is_cicd_enforced,
            is_dag_deploy_enabled=is_dag_deploy_enabled,
            is_high_availability=is_high_availability,
            name=name,
            scheduler_size=scheduler_size,
            type_=type_,
            workspace_id=workspace_id,
            contact_emails=contact_emails,
            default_task_pod_cpu=default_task_pod_cpu,
            default_task_pod_memory=default_task_pod_memory,
            description=description,
            is_development_mode=is_development_mode,
            remote_execution=remote_execution,
            resource_quota_cpu=resource_quota_cpu,
            resource_quota_memory=resource_quota_memory,
            scaling_spec=scaling_spec,
            worker_queues=worker_queues,
            workload_identity=workload_identity,
        )

        update_standard_deployment_request.additional_properties = d
        return update_standard_deployment_request

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
