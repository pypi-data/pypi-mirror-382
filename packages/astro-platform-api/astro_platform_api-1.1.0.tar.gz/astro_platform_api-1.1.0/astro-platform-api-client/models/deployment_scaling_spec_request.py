from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.deployment_hibernation_spec_request import DeploymentHibernationSpecRequest


T = TypeVar("T", bound="DeploymentScalingSpecRequest")


@_attrs_define
class DeploymentScalingSpecRequest:
    """
    Attributes:
        hibernation_spec (Union[Unset, DeploymentHibernationSpecRequest]):
    """

    hibernation_spec: Union[Unset, "DeploymentHibernationSpecRequest"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        hibernation_spec: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.hibernation_spec, Unset):
            hibernation_spec = self.hibernation_spec.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hibernation_spec is not UNSET:
            field_dict["hibernationSpec"] = hibernation_spec

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.deployment_hibernation_spec_request import DeploymentHibernationSpecRequest

        d = dict(src_dict)
        _hibernation_spec = d.pop("hibernationSpec", UNSET)
        hibernation_spec: Union[Unset, DeploymentHibernationSpecRequest]
        if isinstance(_hibernation_spec, Unset):
            hibernation_spec = UNSET
        else:
            hibernation_spec = DeploymentHibernationSpecRequest.from_dict(_hibernation_spec)

        deployment_scaling_spec_request = cls(
            hibernation_spec=hibernation_spec,
        )

        deployment_scaling_spec_request.additional_properties = d
        return deployment_scaling_spec_request

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
