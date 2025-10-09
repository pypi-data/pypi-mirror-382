from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_standard_deployment_request_cloud_provider import CreateStandardDeploymentRequestCloudProvider
from ..models.create_standard_deployment_request_executor import CreateStandardDeploymentRequestExecutor
from ..models.create_standard_deployment_request_scheduler_size import CreateStandardDeploymentRequestSchedulerSize
from ..models.create_standard_deployment_request_type import CreateStandardDeploymentRequestType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.deployment_environment_variable_request import DeploymentEnvironmentVariableRequest
    from ..models.deployment_remote_execution_request import DeploymentRemoteExecutionRequest
    from ..models.deployment_scaling_spec_request import DeploymentScalingSpecRequest
    from ..models.worker_queue_request import WorkerQueueRequest


T = TypeVar("T", bound="CreateStandardDeploymentRequest")


@_attrs_define
class CreateStandardDeploymentRequest:
    """
    Attributes:
        astro_runtime_version (str): Deployment's Astro Runtime version. Example: 9.1.0.
        executor (CreateStandardDeploymentRequestExecutor): The Deployment's executor type. Example: CELERY.
        is_cicd_enforced (bool): Whether the Deployment requires that all deploys are made through CI/CD. Example: True.
        is_dag_deploy_enabled (bool): Whether the Deployment has DAG deploys enabled. Example: True.
        is_high_availability (bool): Whether the Deployment is configured for high availability. If `true`, multiple
            scheduler pods will be online. Example: True.
        name (str): The Deployment's name. Example: My deployment.
        scheduler_size (CreateStandardDeploymentRequestSchedulerSize): The size of the scheduler Pod. Example: MEDIUM.
        type_ (CreateStandardDeploymentRequestType): The type of the Deployment. Example: DEDICATED.
        workspace_id (str): The ID of the Workspace to which the Deployment belongs. Example: clmh8ol3x000008jo656y4285.
        cloud_provider (Union[Unset, CreateStandardDeploymentRequestCloudProvider]): The cloud provider for the
            Deployment's cluster. Optional if `ClusterId` is specified. Example: GCP.
        cluster_id (Union[Unset, str]): The ID of the cluster to which the Deployment will be created in. Optional if
            cloud provider and region is specified. Example: clmh93n2n000008ms3tv79voh.
        contact_emails (Union[Unset, list[str]]): A list of contact emails for the Deployment. Example:
            ['user1@company.com'].
        default_task_pod_cpu (Union[Unset, str]): The default CPU resource usage for a worker Pod when running the
            Kubernetes executor or KubernetesPodOperator. Units are in number of CPU cores. Required if Remote Execution is
            disabled. Example: 0.5.
        default_task_pod_memory (Union[Unset, str]): The default memory resource usage for a worker Pod when running the
            Kubernetes executor or KubernetesPodOperator. Units are in `Gi` and must be explicitly included. This value must
            always be twice the value of `DefaultTaskPodCpu`. Required if Remote Execution is disabled. Example: 1Gi.
        description (Union[Unset, str]): The Deployment's description. Example: My deployment description.
        environment_variables (Union[Unset, list['DeploymentEnvironmentVariableRequest']]): List of environment
            variables to add to the Deployment.
        is_development_mode (Union[Unset, bool]): If true, deployment will be able to use development-only features,
            such as hibernation, but will not have guaranteed uptime SLAs
        region (Union[Unset, str]): The region to host the Deployment in. Optional if `ClusterId` is specified. Example:
            us-east4.
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

    astro_runtime_version: str
    executor: CreateStandardDeploymentRequestExecutor
    is_cicd_enforced: bool
    is_dag_deploy_enabled: bool
    is_high_availability: bool
    name: str
    scheduler_size: CreateStandardDeploymentRequestSchedulerSize
    type_: CreateStandardDeploymentRequestType
    workspace_id: str
    cloud_provider: Union[Unset, CreateStandardDeploymentRequestCloudProvider] = UNSET
    cluster_id: Union[Unset, str] = UNSET
    contact_emails: Union[Unset, list[str]] = UNSET
    default_task_pod_cpu: Union[Unset, str] = UNSET
    default_task_pod_memory: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    environment_variables: Union[Unset, list["DeploymentEnvironmentVariableRequest"]] = UNSET
    is_development_mode: Union[Unset, bool] = UNSET
    region: Union[Unset, str] = UNSET
    remote_execution: Union[Unset, "DeploymentRemoteExecutionRequest"] = UNSET
    resource_quota_cpu: Union[Unset, str] = UNSET
    resource_quota_memory: Union[Unset, str] = UNSET
    scaling_spec: Union[Unset, "DeploymentScalingSpecRequest"] = UNSET
    worker_queues: Union[Unset, list["WorkerQueueRequest"]] = UNSET
    workload_identity: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        astro_runtime_version = self.astro_runtime_version

        executor = self.executor.value

        is_cicd_enforced = self.is_cicd_enforced

        is_dag_deploy_enabled = self.is_dag_deploy_enabled

        is_high_availability = self.is_high_availability

        name = self.name

        scheduler_size = self.scheduler_size.value

        type_ = self.type_.value

        workspace_id = self.workspace_id

        cloud_provider: Union[Unset, str] = UNSET
        if not isinstance(self.cloud_provider, Unset):
            cloud_provider = self.cloud_provider.value

        cluster_id = self.cluster_id

        contact_emails: Union[Unset, list[str]] = UNSET
        if not isinstance(self.contact_emails, Unset):
            contact_emails = self.contact_emails

        default_task_pod_cpu = self.default_task_pod_cpu

        default_task_pod_memory = self.default_task_pod_memory

        description = self.description

        environment_variables: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.environment_variables, Unset):
            environment_variables = []
            for environment_variables_item_data in self.environment_variables:
                environment_variables_item = environment_variables_item_data.to_dict()
                environment_variables.append(environment_variables_item)

        is_development_mode = self.is_development_mode

        region = self.region

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
                "astroRuntimeVersion": astro_runtime_version,
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
        if cloud_provider is not UNSET:
            field_dict["cloudProvider"] = cloud_provider
        if cluster_id is not UNSET:
            field_dict["clusterId"] = cluster_id
        if contact_emails is not UNSET:
            field_dict["contactEmails"] = contact_emails
        if default_task_pod_cpu is not UNSET:
            field_dict["defaultTaskPodCpu"] = default_task_pod_cpu
        if default_task_pod_memory is not UNSET:
            field_dict["defaultTaskPodMemory"] = default_task_pod_memory
        if description is not UNSET:
            field_dict["description"] = description
        if environment_variables is not UNSET:
            field_dict["environmentVariables"] = environment_variables
        if is_development_mode is not UNSET:
            field_dict["isDevelopmentMode"] = is_development_mode
        if region is not UNSET:
            field_dict["region"] = region
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
        astro_runtime_version = d.pop("astroRuntimeVersion")

        executor = CreateStandardDeploymentRequestExecutor(d.pop("executor"))

        is_cicd_enforced = d.pop("isCicdEnforced")

        is_dag_deploy_enabled = d.pop("isDagDeployEnabled")

        is_high_availability = d.pop("isHighAvailability")

        name = d.pop("name")

        scheduler_size = CreateStandardDeploymentRequestSchedulerSize(d.pop("schedulerSize"))

        type_ = CreateStandardDeploymentRequestType(d.pop("type"))

        workspace_id = d.pop("workspaceId")

        _cloud_provider = d.pop("cloudProvider", UNSET)
        cloud_provider: Union[Unset, CreateStandardDeploymentRequestCloudProvider]
        if isinstance(_cloud_provider, Unset):
            cloud_provider = UNSET
        else:
            cloud_provider = CreateStandardDeploymentRequestCloudProvider(_cloud_provider)

        cluster_id = d.pop("clusterId", UNSET)

        contact_emails = cast(list[str], d.pop("contactEmails", UNSET))

        default_task_pod_cpu = d.pop("defaultTaskPodCpu", UNSET)

        default_task_pod_memory = d.pop("defaultTaskPodMemory", UNSET)

        description = d.pop("description", UNSET)

        environment_variables = []
        _environment_variables = d.pop("environmentVariables", UNSET)
        for environment_variables_item_data in _environment_variables or []:
            environment_variables_item = DeploymentEnvironmentVariableRequest.from_dict(environment_variables_item_data)

            environment_variables.append(environment_variables_item)

        is_development_mode = d.pop("isDevelopmentMode", UNSET)

        region = d.pop("region", UNSET)

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

        create_standard_deployment_request = cls(
            astro_runtime_version=astro_runtime_version,
            executor=executor,
            is_cicd_enforced=is_cicd_enforced,
            is_dag_deploy_enabled=is_dag_deploy_enabled,
            is_high_availability=is_high_availability,
            name=name,
            scheduler_size=scheduler_size,
            type_=type_,
            workspace_id=workspace_id,
            cloud_provider=cloud_provider,
            cluster_id=cluster_id,
            contact_emails=contact_emails,
            default_task_pod_cpu=default_task_pod_cpu,
            default_task_pod_memory=default_task_pod_memory,
            description=description,
            environment_variables=environment_variables,
            is_development_mode=is_development_mode,
            region=region,
            remote_execution=remote_execution,
            resource_quota_cpu=resource_quota_cpu,
            resource_quota_memory=resource_quota_memory,
            scaling_spec=scaling_spec,
            worker_queues=worker_queues,
            workload_identity=workload_identity,
        )

        create_standard_deployment_request.additional_properties = d
        return create_standard_deployment_request

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
