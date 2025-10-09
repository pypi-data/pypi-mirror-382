from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.deployment_hibernation_status import DeploymentHibernationStatus


T = TypeVar("T", bound="DeploymentScalingStatus")


@_attrs_define
class DeploymentScalingStatus:
    """
    Attributes:
        hibernation_status (Union[Unset, DeploymentHibernationStatus]):
    """

    hibernation_status: Union[Unset, "DeploymentHibernationStatus"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        hibernation_status: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.hibernation_status, Unset):
            hibernation_status = self.hibernation_status.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hibernation_status is not UNSET:
            field_dict["hibernationStatus"] = hibernation_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.deployment_hibernation_status import DeploymentHibernationStatus

        d = dict(src_dict)
        _hibernation_status = d.pop("hibernationStatus", UNSET)
        hibernation_status: Union[Unset, DeploymentHibernationStatus]
        if isinstance(_hibernation_status, Unset):
            hibernation_status = UNSET
        else:
            hibernation_status = DeploymentHibernationStatus.from_dict(_hibernation_status)

        deployment_scaling_status = cls(
            hibernation_status=hibernation_status,
        )

        deployment_scaling_status.additional_properties = d
        return deployment_scaling_status

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
