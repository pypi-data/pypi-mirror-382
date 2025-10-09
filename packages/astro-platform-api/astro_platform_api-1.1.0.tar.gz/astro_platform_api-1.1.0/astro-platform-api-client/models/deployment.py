import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.deployment_cloud_provider import DeploymentCloudProvider
from ..models.deployment_executor import DeploymentExecutor
from ..models.deployment_scheduler_size import DeploymentSchedulerSize
from ..models.deployment_status import DeploymentStatus
from ..models.deployment_type import DeploymentType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.basic_subject_profile import BasicSubjectProfile
    from ..models.deployment_environment_variable import DeploymentEnvironmentVariable
    from ..models.deployment_remote_execution import DeploymentRemoteExecution
    from ..models.deployment_scaling_spec import DeploymentScalingSpec
    from ..models.deployment_scaling_status import DeploymentScalingStatus
    from ..models.worker_queue import WorkerQueue


T = TypeVar("T", bound="Deployment")


@_attrs_define
class Deployment:
    """
    Attributes:
        airflow_version (str): The Deployment's Airflow version. Example: 2.7.2, if airflow version is not found, it
            will return NA.
        api_url (str): The base URL to directly access the Airflow API. Example:
            https://clypw7uah05jb01nwtpojz0j2.astronomer.run/d4yjo9ed/api/v1.
        astro_runtime_version (str): The Deployment's Astro Runtime version. Example: 9.1.0.
        created_at (datetime.datetime): The time when the Deployment was created in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        created_by (BasicSubjectProfile):
        id (str): The Deployment's ID. Example: clmh57jtm000008lb58fe2wmv.
        image_repository (str): The URL of the Deployment's image repository. Example: https://my-image-repository.
        image_tag (str): The Deployment's custom image tag. Appears only if specified in the most recent deploy.
            Example: my-image-tag.
        is_cicd_enforced (bool): Whether the Deployment requires that all deploys are made through CI/CD. Example: True.
        is_dag_deploy_enabled (bool): Whether the Deployment has DAG deploys enabled. Example: True.
        name (str): The Deployment's name. Example: My deployment.
        namespace (str): The Deployment's namespace name in the Kubernetes cluster. Example: weightless-diameter-8927.
        organization_id (str): The ID of the Organization to which the Deployment belongs. Example:
            clmh59gt0000308lbgswe5fvh.
        runtime_version (str): Deprecated: runtimeVersion has been replaced with astroRuntimeVersion Example: 9.1.0.
        scheduler_cpu (str): The CPU limit for the Deployment's scheduler. Specified in number of CPU cores. Example: 1.
        scheduler_memory (str): The memory limit for the Deployment's scheduler. Units in Gibibytes or `Gi`. Example:
            1Gi.
        scheduler_replicas (int): The number of schedulers to use in the Deployment. Example: 1.
        status (DeploymentStatus): The status of the Deployment. Example: HEALTHY.
        ui_url (str): The URL to access the Airflow UI. Example:
            https://clypw7uah05jb01nwtpojz0j2.astronomer.run/d4yjo9ed?orgId=org_bvqayGttQauxdxB2.
        updated_at (datetime.datetime): The time when the Deployment was last updated in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        updated_by (BasicSubjectProfile):
        web_server_airflow_api_url (str): The Deployment's webserver's base url to directly access the Airflow api.
            Example: myorganization.astronomer-dev.run/d8fe2wmv/api/v1.
        web_server_cpu (str): The CPU limit for the Deployment's webserver. Units are in number of CPU cores. Example:
            0.5.
        web_server_ingress_hostname (str): The Deployment's webserver's ingress hostname. Example:
            clmh597sg000208lb2kjhcn8q.astronomer.run/d8fe2wmv.
        web_server_memory (str): The memory limit for the Deployment's webserver. Units in Gibibytes or `Gi`. Example:
            0.5Gi.
        web_server_url (str): The Deployment's webserver's url. Example: myorganization.astronomer-
            dev.run/d8fe2wmv?orgId=org_edxLzpFcLrgEfpD5.
        workspace_id (str): The ID of the Workspace to which the Deployment belongs. Example:
            clmh58o7d000108lb74ktc9o64.
        cloud_provider (Union[Unset, DeploymentCloudProvider]): The cloud provider of the cluster. Only for Standard
            Deployment. Example: AZURE.
        cluster_id (Union[Unset, str]): The ID of the cluster where the Deployment is hosted. Example:
            clmh597sg000208lb2kjhcn8q.
        cluster_name (Union[Unset, str]): The name of the cluster where the Deployment is hosted. Only for Dedicated and
            Hybrid Deployments. Example: my cluster.
        contact_emails (Union[Unset, list[str]]): The list of contact emails for the Deployment. Example:
            ['user1@company.com'].
        dag_tarball_version (Union[Unset, str]): The Deployment's current DAG tarball version, also known as the Bundle
            Version in the Astro UI. If no deploys are currently processing, this value should be the same as
            DesiredDagTarballVersion. Example: 2024-01-12T18:32:20.5898930Z.
        default_task_pod_cpu (Union[Unset, str]): The default CPU resource usage for a worker Pod when running the
            Kubernetes executor or KubernetesPodOperator. Units are in number of CPU cores. Example: 0.5.
        default_task_pod_memory (Union[Unset, str]): The default memory resource usage for a worker Pod when running the
            Kubernetes executor or KubernetesPodOperator. Units are in `Gi`. This value must always be twice the value of
            `DefaultTaskPodCpu`. Example: 1Gi.
        description (Union[Unset, str]): The Deployment's description. Example: My deployment description.
        desired_dag_tarball_version (Union[Unset, str]): The Deployment's expected DAG tarball version after a currently
            processing deploy completes. This value is updated when a user triggers a DAG-only deploy to indicate that the
            Deployment is expecting a new DAG tarball version. If no deploys are currently processing, this value should be
            the same as DagTarballVersion. Example: 2024-01-12T18:32:20.5898930Z.
        environment_variables (Union[Unset, list['DeploymentEnvironmentVariable']]): The Deployment's environment
            variables. Secret values will be omitted from response.
        executor (Union[Unset, DeploymentExecutor]): The Deployment's executor type. Example: CELERY.
        external_i_ps (Union[Unset, list[str]]): A list of the Deployment's external IPs. Example: ['0.0.0.0'].
        image_version (Union[Unset, str]): A tag that Astronomer applies to the Deployment's Astro Runtime image during
            a deploy. It includes the date and time of the deploy. Example: deploy-2023-09-14T19-04.
        is_development_mode (Union[Unset, bool]): If true, deployment will be able to use development-only features,
            such as hibernation, but will not have guaranteed uptime SLAs
        is_high_availability (Union[Unset, bool]): Whether the Deployment has high availability (HA) enabled. If `true`,
            multiple scheduler Pods will run at once. Example: True.
        oidc_issuer_url (Union[Unset, str]): OIDC issuer URL of the deployment's cluster Example:
            https://westus2.oic.prod-
            aks.azure.com/b84efac8-cfee-467a-b223-23b9aea1486d/3075f79e-abc2-4602-a691-28117197e83d/.
        region (Union[Unset, str]): The region of the cluster. Only for Dedicated and Hybrid Deployments. Example: us-
            east-1.
        remote_execution (Union[Unset, DeploymentRemoteExecution]):
        resource_quota_cpu (Union[Unset, str]): The CPU quota for worker Pods when running the Kubernetes executor or
            KubernetesPodOperator. If current CPU usage across all workers exceeds the quota, no new worker Pods can be
            scheduled. Units are in number of CPU cores. Example: 160.
        resource_quota_memory (Union[Unset, str]): The memory quota for worker Pods when running the Kubernetes executor
            or KubernetesPodOperator. If current memory usage across all workers exceeds the quota, no new worker Pods can
            be scheduled. Units are in `Gi`. This value must always be twice the value of `ResourceQuotaCpu`. Example:
            320Gi.
        scaling_spec (Union[Unset, DeploymentScalingSpec]):
        scaling_status (Union[Unset, DeploymentScalingStatus]):
        scheduler_au (Union[Unset, int]): The number of Astronomer units (AU) for the Deployment's scheduler. Applies
            only to Deployments hosted on Hybrid clusters. Example: 5.
        scheduler_size (Union[Unset, DeploymentSchedulerSize]): The Deployment's scheduler size. Example: MEDIUM.
        status_reason (Union[Unset, str]): A message that provides context for the Deployment's status. Example:
            Successfully Deployed.
        task_pod_node_pool_id (Union[Unset, str]): The node pool ID for the task pod. Example:
            clmh5mash000008mia6lnbs0f.
        type_ (Union[Unset, DeploymentType]): The type of cluster that the Deployment runs on. Example: DEDICATED.
        web_server_replicas (Union[Unset, int]): The number of webserver replicas. Example: 1.
        worker_queues (Union[Unset, list['WorkerQueue']]): A list of the Deployment's worker queues.
        workload_identity (Union[Unset, str]): The Deployment's workload identity.
        workspace_name (Union[Unset, str]): The name of the Workspace to which the Deployment belongs. Example: my-
            workspace.
    """

    airflow_version: str
    api_url: str
    astro_runtime_version: str
    created_at: datetime.datetime
    created_by: "BasicSubjectProfile"
    id: str
    image_repository: str
    image_tag: str
    is_cicd_enforced: bool
    is_dag_deploy_enabled: bool
    name: str
    namespace: str
    organization_id: str
    runtime_version: str
    scheduler_cpu: str
    scheduler_memory: str
    scheduler_replicas: int
    status: DeploymentStatus
    ui_url: str
    updated_at: datetime.datetime
    updated_by: "BasicSubjectProfile"
    web_server_airflow_api_url: str
    web_server_cpu: str
    web_server_ingress_hostname: str
    web_server_memory: str
    web_server_url: str
    workspace_id: str
    cloud_provider: Union[Unset, DeploymentCloudProvider] = UNSET
    cluster_id: Union[Unset, str] = UNSET
    cluster_name: Union[Unset, str] = UNSET
    contact_emails: Union[Unset, list[str]] = UNSET
    dag_tarball_version: Union[Unset, str] = UNSET
    default_task_pod_cpu: Union[Unset, str] = UNSET
    default_task_pod_memory: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    desired_dag_tarball_version: Union[Unset, str] = UNSET
    environment_variables: Union[Unset, list["DeploymentEnvironmentVariable"]] = UNSET
    executor: Union[Unset, DeploymentExecutor] = UNSET
    external_i_ps: Union[Unset, list[str]] = UNSET
    image_version: Union[Unset, str] = UNSET
    is_development_mode: Union[Unset, bool] = UNSET
    is_high_availability: Union[Unset, bool] = UNSET
    oidc_issuer_url: Union[Unset, str] = UNSET
    region: Union[Unset, str] = UNSET
    remote_execution: Union[Unset, "DeploymentRemoteExecution"] = UNSET
    resource_quota_cpu: Union[Unset, str] = UNSET
    resource_quota_memory: Union[Unset, str] = UNSET
    scaling_spec: Union[Unset, "DeploymentScalingSpec"] = UNSET
    scaling_status: Union[Unset, "DeploymentScalingStatus"] = UNSET
    scheduler_au: Union[Unset, int] = UNSET
    scheduler_size: Union[Unset, DeploymentSchedulerSize] = UNSET
    status_reason: Union[Unset, str] = UNSET
    task_pod_node_pool_id: Union[Unset, str] = UNSET
    type_: Union[Unset, DeploymentType] = UNSET
    web_server_replicas: Union[Unset, int] = UNSET
    worker_queues: Union[Unset, list["WorkerQueue"]] = UNSET
    workload_identity: Union[Unset, str] = UNSET
    workspace_name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        airflow_version = self.airflow_version

        api_url = self.api_url

        astro_runtime_version = self.astro_runtime_version

        created_at = self.created_at.isoformat()

        created_by = self.created_by.to_dict()

        id = self.id

        image_repository = self.image_repository

        image_tag = self.image_tag

        is_cicd_enforced = self.is_cicd_enforced

        is_dag_deploy_enabled = self.is_dag_deploy_enabled

        name = self.name

        namespace = self.namespace

        organization_id = self.organization_id

        runtime_version = self.runtime_version

        scheduler_cpu = self.scheduler_cpu

        scheduler_memory = self.scheduler_memory

        scheduler_replicas = self.scheduler_replicas

        status = self.status.value

        ui_url = self.ui_url

        updated_at = self.updated_at.isoformat()

        updated_by = self.updated_by.to_dict()

        web_server_airflow_api_url = self.web_server_airflow_api_url

        web_server_cpu = self.web_server_cpu

        web_server_ingress_hostname = self.web_server_ingress_hostname

        web_server_memory = self.web_server_memory

        web_server_url = self.web_server_url

        workspace_id = self.workspace_id

        cloud_provider: Union[Unset, str] = UNSET
        if not isinstance(self.cloud_provider, Unset):
            cloud_provider = self.cloud_provider.value

        cluster_id = self.cluster_id

        cluster_name = self.cluster_name

        contact_emails: Union[Unset, list[str]] = UNSET
        if not isinstance(self.contact_emails, Unset):
            contact_emails = self.contact_emails

        dag_tarball_version = self.dag_tarball_version

        default_task_pod_cpu = self.default_task_pod_cpu

        default_task_pod_memory = self.default_task_pod_memory

        description = self.description

        desired_dag_tarball_version = self.desired_dag_tarball_version

        environment_variables: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.environment_variables, Unset):
            environment_variables = []
            for environment_variables_item_data in self.environment_variables:
                environment_variables_item = environment_variables_item_data.to_dict()
                environment_variables.append(environment_variables_item)

        executor: Union[Unset, str] = UNSET
        if not isinstance(self.executor, Unset):
            executor = self.executor.value

        external_i_ps: Union[Unset, list[str]] = UNSET
        if not isinstance(self.external_i_ps, Unset):
            external_i_ps = self.external_i_ps

        image_version = self.image_version

        is_development_mode = self.is_development_mode

        is_high_availability = self.is_high_availability

        oidc_issuer_url = self.oidc_issuer_url

        region = self.region

        remote_execution: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.remote_execution, Unset):
            remote_execution = self.remote_execution.to_dict()

        resource_quota_cpu = self.resource_quota_cpu

        resource_quota_memory = self.resource_quota_memory

        scaling_spec: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.scaling_spec, Unset):
            scaling_spec = self.scaling_spec.to_dict()

        scaling_status: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.scaling_status, Unset):
            scaling_status = self.scaling_status.to_dict()

        scheduler_au = self.scheduler_au

        scheduler_size: Union[Unset, str] = UNSET
        if not isinstance(self.scheduler_size, Unset):
            scheduler_size = self.scheduler_size.value

        status_reason = self.status_reason

        task_pod_node_pool_id = self.task_pod_node_pool_id

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        web_server_replicas = self.web_server_replicas

        worker_queues: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.worker_queues, Unset):
            worker_queues = []
            for worker_queues_item_data in self.worker_queues:
                worker_queues_item = worker_queues_item_data.to_dict()
                worker_queues.append(worker_queues_item)

        workload_identity = self.workload_identity

        workspace_name = self.workspace_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "airflowVersion": airflow_version,
                "apiUrl": api_url,
                "astroRuntimeVersion": astro_runtime_version,
                "createdAt": created_at,
                "createdBy": created_by,
                "id": id,
                "imageRepository": image_repository,
                "imageTag": image_tag,
                "isCicdEnforced": is_cicd_enforced,
                "isDagDeployEnabled": is_dag_deploy_enabled,
                "name": name,
                "namespace": namespace,
                "organizationId": organization_id,
                "runtimeVersion": runtime_version,
                "schedulerCpu": scheduler_cpu,
                "schedulerMemory": scheduler_memory,
                "schedulerReplicas": scheduler_replicas,
                "status": status,
                "uiUrl": ui_url,
                "updatedAt": updated_at,
                "updatedBy": updated_by,
                "webServerAirflowApiUrl": web_server_airflow_api_url,
                "webServerCpu": web_server_cpu,
                "webServerIngressHostname": web_server_ingress_hostname,
                "webServerMemory": web_server_memory,
                "webServerUrl": web_server_url,
                "workspaceId": workspace_id,
            }
        )
        if cloud_provider is not UNSET:
            field_dict["cloudProvider"] = cloud_provider
        if cluster_id is not UNSET:
            field_dict["clusterId"] = cluster_id
        if cluster_name is not UNSET:
            field_dict["clusterName"] = cluster_name
        if contact_emails is not UNSET:
            field_dict["contactEmails"] = contact_emails
        if dag_tarball_version is not UNSET:
            field_dict["dagTarballVersion"] = dag_tarball_version
        if default_task_pod_cpu is not UNSET:
            field_dict["defaultTaskPodCpu"] = default_task_pod_cpu
        if default_task_pod_memory is not UNSET:
            field_dict["defaultTaskPodMemory"] = default_task_pod_memory
        if description is not UNSET:
            field_dict["description"] = description
        if desired_dag_tarball_version is not UNSET:
            field_dict["desiredDagTarballVersion"] = desired_dag_tarball_version
        if environment_variables is not UNSET:
            field_dict["environmentVariables"] = environment_variables
        if executor is not UNSET:
            field_dict["executor"] = executor
        if external_i_ps is not UNSET:
            field_dict["externalIPs"] = external_i_ps
        if image_version is not UNSET:
            field_dict["imageVersion"] = image_version
        if is_development_mode is not UNSET:
            field_dict["isDevelopmentMode"] = is_development_mode
        if is_high_availability is not UNSET:
            field_dict["isHighAvailability"] = is_high_availability
        if oidc_issuer_url is not UNSET:
            field_dict["oidcIssuerUrl"] = oidc_issuer_url
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
        if scaling_status is not UNSET:
            field_dict["scalingStatus"] = scaling_status
        if scheduler_au is not UNSET:
            field_dict["schedulerAu"] = scheduler_au
        if scheduler_size is not UNSET:
            field_dict["schedulerSize"] = scheduler_size
        if status_reason is not UNSET:
            field_dict["statusReason"] = status_reason
        if task_pod_node_pool_id is not UNSET:
            field_dict["taskPodNodePoolId"] = task_pod_node_pool_id
        if type_ is not UNSET:
            field_dict["type"] = type_
        if web_server_replicas is not UNSET:
            field_dict["webServerReplicas"] = web_server_replicas
        if worker_queues is not UNSET:
            field_dict["workerQueues"] = worker_queues
        if workload_identity is not UNSET:
            field_dict["workloadIdentity"] = workload_identity
        if workspace_name is not UNSET:
            field_dict["workspaceName"] = workspace_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.basic_subject_profile import BasicSubjectProfile
        from ..models.deployment_environment_variable import DeploymentEnvironmentVariable
        from ..models.deployment_remote_execution import DeploymentRemoteExecution
        from ..models.deployment_scaling_spec import DeploymentScalingSpec
        from ..models.deployment_scaling_status import DeploymentScalingStatus
        from ..models.worker_queue import WorkerQueue

        d = dict(src_dict)
        airflow_version = d.pop("airflowVersion")

        api_url = d.pop("apiUrl")

        astro_runtime_version = d.pop("astroRuntimeVersion")

        created_at = isoparse(d.pop("createdAt"))

        created_by = BasicSubjectProfile.from_dict(d.pop("createdBy"))

        id = d.pop("id")

        image_repository = d.pop("imageRepository")

        image_tag = d.pop("imageTag")

        is_cicd_enforced = d.pop("isCicdEnforced")

        is_dag_deploy_enabled = d.pop("isDagDeployEnabled")

        name = d.pop("name")

        namespace = d.pop("namespace")

        organization_id = d.pop("organizationId")

        runtime_version = d.pop("runtimeVersion")

        scheduler_cpu = d.pop("schedulerCpu")

        scheduler_memory = d.pop("schedulerMemory")

        scheduler_replicas = d.pop("schedulerReplicas")

        status = DeploymentStatus(d.pop("status"))

        ui_url = d.pop("uiUrl")

        updated_at = isoparse(d.pop("updatedAt"))

        updated_by = BasicSubjectProfile.from_dict(d.pop("updatedBy"))

        web_server_airflow_api_url = d.pop("webServerAirflowApiUrl")

        web_server_cpu = d.pop("webServerCpu")

        web_server_ingress_hostname = d.pop("webServerIngressHostname")

        web_server_memory = d.pop("webServerMemory")

        web_server_url = d.pop("webServerUrl")

        workspace_id = d.pop("workspaceId")

        _cloud_provider = d.pop("cloudProvider", UNSET)
        cloud_provider: Union[Unset, DeploymentCloudProvider]
        if isinstance(_cloud_provider, Unset):
            cloud_provider = UNSET
        else:
            cloud_provider = DeploymentCloudProvider(_cloud_provider)

        cluster_id = d.pop("clusterId", UNSET)

        cluster_name = d.pop("clusterName", UNSET)

        contact_emails = cast(list[str], d.pop("contactEmails", UNSET))

        dag_tarball_version = d.pop("dagTarballVersion", UNSET)

        default_task_pod_cpu = d.pop("defaultTaskPodCpu", UNSET)

        default_task_pod_memory = d.pop("defaultTaskPodMemory", UNSET)

        description = d.pop("description", UNSET)

        desired_dag_tarball_version = d.pop("desiredDagTarballVersion", UNSET)

        environment_variables = []
        _environment_variables = d.pop("environmentVariables", UNSET)
        for environment_variables_item_data in _environment_variables or []:
            environment_variables_item = DeploymentEnvironmentVariable.from_dict(environment_variables_item_data)

            environment_variables.append(environment_variables_item)

        _executor = d.pop("executor", UNSET)
        executor: Union[Unset, DeploymentExecutor]
        if isinstance(_executor, Unset):
            executor = UNSET
        else:
            executor = DeploymentExecutor(_executor)

        external_i_ps = cast(list[str], d.pop("externalIPs", UNSET))

        image_version = d.pop("imageVersion", UNSET)

        is_development_mode = d.pop("isDevelopmentMode", UNSET)

        is_high_availability = d.pop("isHighAvailability", UNSET)

        oidc_issuer_url = d.pop("oidcIssuerUrl", UNSET)

        region = d.pop("region", UNSET)

        _remote_execution = d.pop("remoteExecution", UNSET)
        remote_execution: Union[Unset, DeploymentRemoteExecution]
        if isinstance(_remote_execution, Unset):
            remote_execution = UNSET
        else:
            remote_execution = DeploymentRemoteExecution.from_dict(_remote_execution)

        resource_quota_cpu = d.pop("resourceQuotaCpu", UNSET)

        resource_quota_memory = d.pop("resourceQuotaMemory", UNSET)

        _scaling_spec = d.pop("scalingSpec", UNSET)
        scaling_spec: Union[Unset, DeploymentScalingSpec]
        if isinstance(_scaling_spec, Unset):
            scaling_spec = UNSET
        else:
            scaling_spec = DeploymentScalingSpec.from_dict(_scaling_spec)

        _scaling_status = d.pop("scalingStatus", UNSET)
        scaling_status: Union[Unset, DeploymentScalingStatus]
        if isinstance(_scaling_status, Unset):
            scaling_status = UNSET
        else:
            scaling_status = DeploymentScalingStatus.from_dict(_scaling_status)

        scheduler_au = d.pop("schedulerAu", UNSET)

        _scheduler_size = d.pop("schedulerSize", UNSET)
        scheduler_size: Union[Unset, DeploymentSchedulerSize]
        if isinstance(_scheduler_size, Unset):
            scheduler_size = UNSET
        else:
            scheduler_size = DeploymentSchedulerSize(_scheduler_size)

        status_reason = d.pop("statusReason", UNSET)

        task_pod_node_pool_id = d.pop("taskPodNodePoolId", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, DeploymentType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = DeploymentType(_type_)

        web_server_replicas = d.pop("webServerReplicas", UNSET)

        worker_queues = []
        _worker_queues = d.pop("workerQueues", UNSET)
        for worker_queues_item_data in _worker_queues or []:
            worker_queues_item = WorkerQueue.from_dict(worker_queues_item_data)

            worker_queues.append(worker_queues_item)

        workload_identity = d.pop("workloadIdentity", UNSET)

        workspace_name = d.pop("workspaceName", UNSET)

        deployment = cls(
            airflow_version=airflow_version,
            api_url=api_url,
            astro_runtime_version=astro_runtime_version,
            created_at=created_at,
            created_by=created_by,
            id=id,
            image_repository=image_repository,
            image_tag=image_tag,
            is_cicd_enforced=is_cicd_enforced,
            is_dag_deploy_enabled=is_dag_deploy_enabled,
            name=name,
            namespace=namespace,
            organization_id=organization_id,
            runtime_version=runtime_version,
            scheduler_cpu=scheduler_cpu,
            scheduler_memory=scheduler_memory,
            scheduler_replicas=scheduler_replicas,
            status=status,
            ui_url=ui_url,
            updated_at=updated_at,
            updated_by=updated_by,
            web_server_airflow_api_url=web_server_airflow_api_url,
            web_server_cpu=web_server_cpu,
            web_server_ingress_hostname=web_server_ingress_hostname,
            web_server_memory=web_server_memory,
            web_server_url=web_server_url,
            workspace_id=workspace_id,
            cloud_provider=cloud_provider,
            cluster_id=cluster_id,
            cluster_name=cluster_name,
            contact_emails=contact_emails,
            dag_tarball_version=dag_tarball_version,
            default_task_pod_cpu=default_task_pod_cpu,
            default_task_pod_memory=default_task_pod_memory,
            description=description,
            desired_dag_tarball_version=desired_dag_tarball_version,
            environment_variables=environment_variables,
            executor=executor,
            external_i_ps=external_i_ps,
            image_version=image_version,
            is_development_mode=is_development_mode,
            is_high_availability=is_high_availability,
            oidc_issuer_url=oidc_issuer_url,
            region=region,
            remote_execution=remote_execution,
            resource_quota_cpu=resource_quota_cpu,
            resource_quota_memory=resource_quota_memory,
            scaling_spec=scaling_spec,
            scaling_status=scaling_status,
            scheduler_au=scheduler_au,
            scheduler_size=scheduler_size,
            status_reason=status_reason,
            task_pod_node_pool_id=task_pod_node_pool_id,
            type_=type_,
            web_server_replicas=web_server_replicas,
            worker_queues=worker_queues,
            workload_identity=workload_identity,
            workspace_name=workspace_name,
        )

        deployment.additional_properties = d
        return deployment

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
