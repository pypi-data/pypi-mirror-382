from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.basic_subject_profile_subject_type import BasicSubjectProfileSubjectType
from ..types import UNSET, Unset

T = TypeVar("T", bound="BasicSubjectProfile")


@_attrs_define
class BasicSubjectProfile:
    """
    Attributes:
        id (str): The subject's ID. Example: clm8qv74h000008mlf08scq7k.
        api_token_name (Union[Unset, str]): The API token's name. Returned only when `SubjectType` is `SERVICEKEY`.
            Example: my-token.
        avatar_url (Union[Unset, str]): The URL for the user's profile image. Returned only when `SubjectType` is
            `USER`. Example: https://avatar.url.
        full_name (Union[Unset, str]): The subject's full name. Returned only when `SubjectType` is `USER`. Example:
            Jane Doe.
        subject_type (Union[Unset, BasicSubjectProfileSubjectType]): The subject type. Example: USER.
        username (Union[Unset, str]): The subject's username. Returned only when `SubjectType` is `USER`. Example:
            user1@company.com.
    """

    id: str
    api_token_name: Union[Unset, str] = UNSET
    avatar_url: Union[Unset, str] = UNSET
    full_name: Union[Unset, str] = UNSET
    subject_type: Union[Unset, BasicSubjectProfileSubjectType] = UNSET
    username: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        api_token_name = self.api_token_name

        avatar_url = self.avatar_url

        full_name = self.full_name

        subject_type: Union[Unset, str] = UNSET
        if not isinstance(self.subject_type, Unset):
            subject_type = self.subject_type.value

        username = self.username

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if api_token_name is not UNSET:
            field_dict["apiTokenName"] = api_token_name
        if avatar_url is not UNSET:
            field_dict["avatarUrl"] = avatar_url
        if full_name is not UNSET:
            field_dict["fullName"] = full_name
        if subject_type is not UNSET:
            field_dict["subjectType"] = subject_type
        if username is not UNSET:
            field_dict["username"] = username

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        api_token_name = d.pop("apiTokenName", UNSET)

        avatar_url = d.pop("avatarUrl", UNSET)

        full_name = d.pop("fullName", UNSET)

        _subject_type = d.pop("subjectType", UNSET)
        subject_type: Union[Unset, BasicSubjectProfileSubjectType]
        if isinstance(_subject_type, Unset):
            subject_type = UNSET
        else:
            subject_type = BasicSubjectProfileSubjectType(_subject_type)

        username = d.pop("username", UNSET)

        basic_subject_profile = cls(
            id=id,
            api_token_name=api_token_name,
            avatar_url=avatar_url,
            full_name=full_name,
            subject_type=subject_type,
            username=username,
        )

        basic_subject_profile.additional_properties = d
        return basic_subject_profile

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
