from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests

from odp.new_client import Client


@dataclass(frozen=True)
class DatasetMeta:
    id: str
    name: str
    description: str

    @classmethod
    def from_dict(cls, data: dict) -> DatasetMeta:
        return DatasetMeta(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
        )


def create_dataset_meta(cli: Client, name: str, description: str = "n/a") -> DatasetMeta:
    """
    Create a new dataset with the given name and description.
    Returns the created Dataset object.
    """
    res = cli._request(
        requests.Request(
            method="POST",
            url=cli.base_url + "/api/catalog/v2/datasets",
            data={
                "name": name,
                "description": description,
            },
        ),
        retry=False,
    )
    res.raise_for_status()
    data = res.json()
    return DatasetMeta.from_dict(data)


def get_dataset_meta_by_name(cli: Client, name: str) -> Optional[DatasetMeta]:
    """
    Fetch a dataset by its name.
    Returns None if the dataset does not exist.
    """
    res = cli._request(
        requests.Request(
            method="GET",
            url=cli.base_url + "/api/catalog/v2/datasets",
        )
    )
    res.raise_for_status()
    for item in res.json():
        if item["name"] == name:
            return DatasetMeta.from_dict(item)

    return None


def get_dataset_meta_by_uuid(cli: Client, uuid: str) -> Optional[DatasetMeta]:
    """
    Fetch a dataset by its UUID.
    Returns None if the dataset does not exist.
    """
    res = cli._request(
        requests.Request(
            method="GET",
            url=cli.base_url + f"/api/catalog/v2/datasets/{uuid}",
        )
    )
    if res.status_code == 404:
        return None

    data = res.json()
    return DatasetMeta.from_dict(data)
