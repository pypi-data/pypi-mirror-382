import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.deploy_status import DeployStatus
from ..models.deploy_type import DeployType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.basic_subject_profile import BasicSubjectProfile
    from ..models.bundle import Bundle


T = TypeVar("T", bound="Deploy")


@_attrs_define
class Deploy:
    """
    Attributes:
        created_at (datetime.datetime): The time when the deploy was created in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        deployment_id (str): The Deployment's ID. Example: clmh57jtm000008lb58fe2wmv.
        id (str): The deploy's ID. Example: clvetru2w000201mowqwua63n.
        image_repository (str): The URL of the deploy's image repository. Example: https://my-image-repository.
        image_tag (str): The deploy's image tag. Appears only if specified in the most recent deploy. Example: my-image-
            tag.
        is_dag_deploy_enabled (bool): Whether the deploy was triggered on a Deployment with DAG deploys enabled.
            Example: True.
        status (DeployStatus): The status of the deploy. Example: DEPLOYED.
        type_ (DeployType): The type of deploy. Example: IMAGE_AND_DAG.
        airflow_version (Union[Unset, str]): The deploy's Airflow version. Example: 2.7.2, if airflow version is not
            found, it will return NA.
        astro_runtime_version (Union[Unset, str]): The deploy's Astro Runtime version. Example: 9.1.0.
        bundle_mount_path (Union[Unset, str]): The path where Astro mounts the bundle on the Airflow component pods.
        bundle_upload_url (Union[Unset, str]): The URL where the deploy uploads the bundle. Appears only if DAG deploys
            are enabled on the Deployment and deploy type is BUNDLE.
        bundles (Union[Unset, list['Bundle']]): The bundles included in a specific Deployment.
        created_by_subject (Union[Unset, BasicSubjectProfile]):
        dag_tarball_version (Union[Unset, str]): The deploy's DAG tarball version, also known as the Bundle Version in
            the Astro UI. Example: 2024-01-12T18:32:20.5898930Z.
        dags_upload_url (Union[Unset, str]): The deploy's upload URL to upload DAG bundles. Appears only if dag deploys
            are enabled on the Deployment. Example:
            https://astroproddagdeploy.windows.core.net/clmh59gt0000308lbgswe5fvh/clmh57jtm000008lb58fe2wmv.
        description (Union[Unset, str]): The deploy's description. Example: My deploy description.
        rollback_from_id (Union[Unset, str]): The ID of the deploy that you completed a rollback on. Appears only if a
            rollback has been performed. Example: clvcz1lrq000101oitxtp276e.
        updated_at (Union[Unset, datetime.datetime]): The time when the deploy was last updated in UTC, formatted as
            `YYYY-MM-DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        updated_by_subject (Union[Unset, BasicSubjectProfile]):
    """

    created_at: datetime.datetime
    deployment_id: str
    id: str
    image_repository: str
    image_tag: str
    is_dag_deploy_enabled: bool
    status: DeployStatus
    type_: DeployType
    airflow_version: Union[Unset, str] = UNSET
    astro_runtime_version: Union[Unset, str] = UNSET
    bundle_mount_path: Union[Unset, str] = UNSET
    bundle_upload_url: Union[Unset, str] = UNSET
    bundles: Union[Unset, list["Bundle"]] = UNSET
    created_by_subject: Union[Unset, "BasicSubjectProfile"] = UNSET
    dag_tarball_version: Union[Unset, str] = UNSET
    dags_upload_url: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    rollback_from_id: Union[Unset, str] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    updated_by_subject: Union[Unset, "BasicSubjectProfile"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at.isoformat()

        deployment_id = self.deployment_id

        id = self.id

        image_repository = self.image_repository

        image_tag = self.image_tag

        is_dag_deploy_enabled = self.is_dag_deploy_enabled

        status = self.status.value

        type_ = self.type_.value

        airflow_version = self.airflow_version

        astro_runtime_version = self.astro_runtime_version

        bundle_mount_path = self.bundle_mount_path

        bundle_upload_url = self.bundle_upload_url

        bundles: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.bundles, Unset):
            bundles = []
            for bundles_item_data in self.bundles:
                bundles_item = bundles_item_data.to_dict()
                bundles.append(bundles_item)

        created_by_subject: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.created_by_subject, Unset):
            created_by_subject = self.created_by_subject.to_dict()

        dag_tarball_version = self.dag_tarball_version

        dags_upload_url = self.dags_upload_url

        description = self.description

        rollback_from_id = self.rollback_from_id

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        updated_by_subject: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.updated_by_subject, Unset):
            updated_by_subject = self.updated_by_subject.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "createdAt": created_at,
                "deploymentId": deployment_id,
                "id": id,
                "imageRepository": image_repository,
                "imageTag": image_tag,
                "isDagDeployEnabled": is_dag_deploy_enabled,
                "status": status,
                "type": type_,
            }
        )
        if airflow_version is not UNSET:
            field_dict["airflowVersion"] = airflow_version
        if astro_runtime_version is not UNSET:
            field_dict["astroRuntimeVersion"] = astro_runtime_version
        if bundle_mount_path is not UNSET:
            field_dict["bundleMountPath"] = bundle_mount_path
        if bundle_upload_url is not UNSET:
            field_dict["bundleUploadUrl"] = bundle_upload_url
        if bundles is not UNSET:
            field_dict["bundles"] = bundles
        if created_by_subject is not UNSET:
            field_dict["createdBySubject"] = created_by_subject
        if dag_tarball_version is not UNSET:
            field_dict["dagTarballVersion"] = dag_tarball_version
        if dags_upload_url is not UNSET:
            field_dict["dagsUploadUrl"] = dags_upload_url
        if description is not UNSET:
            field_dict["description"] = description
        if rollback_from_id is not UNSET:
            field_dict["rollbackFromId"] = rollback_from_id
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at
        if updated_by_subject is not UNSET:
            field_dict["updatedBySubject"] = updated_by_subject

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.basic_subject_profile import BasicSubjectProfile
        from ..models.bundle import Bundle

        d = dict(src_dict)
        created_at = isoparse(d.pop("createdAt"))

        deployment_id = d.pop("deploymentId")

        id = d.pop("id")

        image_repository = d.pop("imageRepository")

        image_tag = d.pop("imageTag")

        is_dag_deploy_enabled = d.pop("isDagDeployEnabled")

        status = DeployStatus(d.pop("status"))

        type_ = DeployType(d.pop("type"))

        airflow_version = d.pop("airflowVersion", UNSET)

        astro_runtime_version = d.pop("astroRuntimeVersion", UNSET)

        bundle_mount_path = d.pop("bundleMountPath", UNSET)

        bundle_upload_url = d.pop("bundleUploadUrl", UNSET)

        bundles = []
        _bundles = d.pop("bundles", UNSET)
        for bundles_item_data in _bundles or []:
            bundles_item = Bundle.from_dict(bundles_item_data)

            bundles.append(bundles_item)

        _created_by_subject = d.pop("createdBySubject", UNSET)
        created_by_subject: Union[Unset, BasicSubjectProfile]
        if isinstance(_created_by_subject, Unset):
            created_by_subject = UNSET
        else:
            created_by_subject = BasicSubjectProfile.from_dict(_created_by_subject)

        dag_tarball_version = d.pop("dagTarballVersion", UNSET)

        dags_upload_url = d.pop("dagsUploadUrl", UNSET)

        description = d.pop("description", UNSET)

        rollback_from_id = d.pop("rollbackFromId", UNSET)

        _updated_at = d.pop("updatedAt", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        _updated_by_subject = d.pop("updatedBySubject", UNSET)
        updated_by_subject: Union[Unset, BasicSubjectProfile]
        if isinstance(_updated_by_subject, Unset):
            updated_by_subject = UNSET
        else:
            updated_by_subject = BasicSubjectProfile.from_dict(_updated_by_subject)

        deploy = cls(
            created_at=created_at,
            deployment_id=deployment_id,
            id=id,
            image_repository=image_repository,
            image_tag=image_tag,
            is_dag_deploy_enabled=is_dag_deploy_enabled,
            status=status,
            type_=type_,
            airflow_version=airflow_version,
            astro_runtime_version=astro_runtime_version,
            bundle_mount_path=bundle_mount_path,
            bundle_upload_url=bundle_upload_url,
            bundles=bundles,
            created_by_subject=created_by_subject,
            dag_tarball_version=dag_tarball_version,
            dags_upload_url=dags_upload_url,
            description=description,
            rollback_from_id=rollback_from_id,
            updated_at=updated_at,
            updated_by_subject=updated_by_subject,
        )

        deploy.additional_properties = d
        return deploy

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
