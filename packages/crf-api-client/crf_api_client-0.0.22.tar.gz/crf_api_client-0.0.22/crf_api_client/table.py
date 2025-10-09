# ruff: noqa: ANN003, D105, EM102, PLR2004, G004
import json
import logging
from typing import Optional

import requests

from .base import BaseAPIClient
from .task import Task

logger = logging.getLogger(__name__)


class Table(BaseAPIClient):
    def __init__(
        self,
        base_url: str,
        token: str,
        warehouse_id: str,
        table_id: str,
        name: str = None,
        **kwargs,
    ):
        super().__init__(base_url, token)
        self.warehouse_id = warehouse_id
        self.table_id = table_id
        self.name = name
        # Store any additional table attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def write_data(
        self,
        data: list[dict],
        override: bool = False,
        table_version_id: Optional[str] = None,
        use_deployed_version: bool = False,
        batch_size: int = 1000,
    ) -> dict:
        """Write data to this table"""
        if isinstance(data, dict):
            data = [data]
        if batch_size:
            batches = [data[i : i + batch_size] for i in range(0, len(data), batch_size)]
            responses = []
            for i, batch in enumerate(batches):
                response = requests.post(
                    f"{self.base_url}/api/v1/projects/{self.warehouse_id}/write-data/?table_name={self.name}",
                    headers=self._get_headers(),
                    json={
                        "table_name": self.name,
                        "data": json.dumps(batch),
                        # Only override on first batch to avoid duplicate overrides
                        "override": override and i == 0,
                        "table_version_id": table_version_id,
                        "use_deployed_version": use_deployed_version,
                    },
                )
                if response.status_code != 200:
                    logger.exception(f"Error writing data for batch: {batch}")
                    responses.append(response.text)
                    continue
                responses.append(response.json())
            return {"status": "success", "batches_responses": responses}

        if isinstance(data, list):
            data = json.dumps(data)
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.warehouse_id}/write-data/?table_name={self.name}",
            headers=self._get_headers(),
            json={
                "table_name": self.name,
                "data": data,
                "override": override,
                "table_version_id": table_version_id,
                "use_deployed_version": use_deployed_version,
            },
        )
        response.raise_for_status()
        return response.json()

    def get_data(
        self,
        offset: int = 0,
        page_size: int = 10000,
        max_results: Optional[int] = None,
        remove_embeddings: bool = True,
        chunk_id: Optional[str] = None,
        document_id: Optional[str] = None,
        object_id: Optional[str] = None,
        table_version_id: Optional[str] = None,
        use_deployed_version: bool = False,
        **kwargs,
    ) -> list[dict]:
        """Download data from this table"""
        params = {
            "table_name": self.name,
            "remove_embeddings": str(remove_embeddings).lower(),
            "offset": offset,
            "limit": page_size,
            "use_deployed_version": str(use_deployed_version).lower(),
            "table_version_id": table_version_id,
        }
        if self.object_type == "chunk" and chunk_id:
            params["id"] = chunk_id
        if chunk_id and self.object_type != "chunk":
            params["chunk_id"] = chunk_id
        if document_id:
            params["document_id"] = document_id
        if object_id:
            params["id"] = object_id
        for key, value in kwargs.items():
            if key.endswith("__in") and isinstance(value, list):
                params[key] = ",".join(value)
            else:
                params[key] = value

        return self._get_paginated_data(
            f"{self.base_url}/api/v1/projects/{self.warehouse_id}/get-data/",
            params=params,
            max_results=max_results,
        )

    def push_to_retrieval(self) -> Optional[Task]:
        if self.object_type == "chunk":
            response = requests.post(
                f"{self.base_url}/api/v1/projects/{self.warehouse_id}/tables/{self.table_id}/push-chunks/",
                headers=self._get_headers(),
                json={},
            )
        elif self.object_type == "tag":
            response = requests.post(
                f"{self.base_url}/api/v1/projects/{self.warehouse_id}/tables/{self.table_id}/push-tags/",
                headers=self._get_headers(),
                json={},
            )
        elif self.object_type == "object":
            response = requests.post(
                f"{self.base_url}/api/v1/projects/{self.warehouse_id}/tables/{self.table_id}/push-objects/",
                headers=self._get_headers(),
                json={},
            )
        else:
            raise ValueError(f"Unsupported object type for push to retrieval: {self.object_type}")
        if response.status_code != 200:
            logger.error(f"Error pushing to retrieval: {response.text}")
            return None
        task_id = response.json().get("pipeline_run_id")
        return Task(self.base_url, self.token, self.warehouse_id, task_id, "pending")

    def list_versions(self) -> list[dict]:
        return self._get_paginated_data(
            f"{self.base_url}/api/v1/projects/{self.warehouse_id}/tables/{self.table_id}/versions/",
        )

    def create_version(self) -> dict:
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.warehouse_id}/tables/{self.table_id}/versions/",
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()

    def delete(self) -> dict:
        return requests.delete(
            f"{self.base_url}/api/v1/projects/{self.warehouse_id}/tables/{self.table_id}/",
            headers=self._get_headers(),
        )

    def set_deployed_version(self, version_id: str) -> dict:
        return requests.post(
            f"{self.base_url}/api/v1/projects/{self.warehouse_id}/tables/{self.table_id}/set-default-version/",
            headers=self._get_headers(),
            json={"version_id": version_id},
        )

    def update_table_version_dependencies(self, dependencies: dict, version_id: str) -> dict:
        response = requests.patch(
            f"{self.base_url}/api/v1/projects/{self.warehouse_id}/tables-versions/{version_id}/",
            headers=self._get_headers(),
            json={"table_version_dependencies": dependencies},
        )
        response.raise_for_status()
        return response.json()

    def __repr__(self):
        return (
            f"Table(id='{self.table_id}', name='{self.name}', warehouse_id='{self.warehouse_id}')"
        )

    def raw(self):
        response = requests.get(
            f"{self.base_url}/api/v1/projects/{self.warehouse_id}/tables/{self.table_id}/",
            headers=self._get_headers(),
        )
        if response.status_code != 200:
            raise ValueError(f"Error getting table: {response.text}")
        return response.json()

    def __str__(self):
        return f"Table: {self.name} ({self.table_id})"
