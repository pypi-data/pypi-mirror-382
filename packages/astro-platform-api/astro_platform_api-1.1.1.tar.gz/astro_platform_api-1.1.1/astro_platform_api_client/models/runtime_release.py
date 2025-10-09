import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="RuntimeRelease")


@_attrs_define
class RuntimeRelease:
    """
    Attributes:
        airflow_database_migration (bool): Whether the release requires an Airflow database migration.
        airflow_version (str): The Airflow version that the Runtime image is based on. Example: 2.7.1.
        channel (str): The release channel. Example: stable.
        release_date (datetime.datetime): The time when the version is released in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        stellar_database_migration (bool): Whether the release requires a Stellar database migration.
        version (str): The Astro Runtime version. Example: 9.1.0.
    """

    airflow_database_migration: bool
    airflow_version: str
    channel: str
    release_date: datetime.datetime
    stellar_database_migration: bool
    version: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        airflow_database_migration = self.airflow_database_migration

        airflow_version = self.airflow_version

        channel = self.channel

        release_date = self.release_date.isoformat()

        stellar_database_migration = self.stellar_database_migration

        version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "airflowDatabaseMigration": airflow_database_migration,
                "airflowVersion": airflow_version,
                "channel": channel,
                "releaseDate": release_date,
                "stellarDatabaseMigration": stellar_database_migration,
                "version": version,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        airflow_database_migration = d.pop("airflowDatabaseMigration")

        airflow_version = d.pop("airflowVersion")

        channel = d.pop("channel")

        release_date = isoparse(d.pop("releaseDate"))

        stellar_database_migration = d.pop("stellarDatabaseMigration")

        version = d.pop("version")

        runtime_release = cls(
            airflow_database_migration=airflow_database_migration,
            airflow_version=airflow_version,
            channel=channel,
            release_date=release_date,
            stellar_database_migration=stellar_database_migration,
            version=version,
        )

        runtime_release.additional_properties = d
        return runtime_release

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
