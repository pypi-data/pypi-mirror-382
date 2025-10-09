# ruff: noqa: PLR2004, TRY002, ARG002, D200, E501
import json
import logging
from typing import Optional

import requests

from .base import BaseAPIClient
from .exception import CRFAPIError
from .operations.client_operations import ClientImportOperations
from .warehouse import Warehouse

logger = logging.getLogger(__name__)


class CRFAPIClient(BaseAPIClient):
    def __init__(self, base_url: str, token: str):
        super().__init__(base_url, token)

    # Warehouse methods
    def list_warehouses(self) -> list[Warehouse]:
        """List all warehouses and return them as Warehouse objects"""
        warehouse_data = self._get_paginated_data(f"{self.base_url}/api/v1/projects/")
        warehouses = []
        for data in warehouse_data:
            warehouse = Warehouse(
                base_url=self.base_url,
                token=self.token,
                id=data.get("id"),
                name=data.get("name"),
                **{k: v for k, v in data.items() if k not in ["id", "name"]},
            )
            warehouses.append(warehouse)
        return warehouses

    def create_warehouse(
        self, name: str, brief: Optional[str] = None, default_llm_model: Optional[str] = None
    ) -> Warehouse:
        """Create a new warehouse and return it as a Warehouse object"""
        if brief is None:
            brief = "Warehouse about " + name
        create_warehouse_payload = {
            "name": name,
            "business_brief": brief,
        }
        if default_llm_model:
            create_warehouse_payload["default_llm_model"] = default_llm_model

        response = requests.post(
            f"{self.base_url}/api/v1/projects/",
            headers=self._get_headers(),
            json=create_warehouse_payload,
        )
        if response.status_code != 201:
            raise CRFAPIError(response.json(), response)
        data = response.json()

        return Warehouse(
            base_url=self.base_url,
            token=self.token,
            name=data.get("name"),
            id=data.get("id"),
            **{k: v for k, v in data.items() if k not in ["id", "name"]},
        )

    def delete_warehouse(
        self,
        warehouse_id: str,
    ) -> dict:
        """Delete a warehouse and its associated Neo4j data."""
        response = requests.delete(
            f"{self.base_url}/api/v1/projects/{warehouse_id}/",
            headers=self._get_headers(),
        )
        if response.status_code != 204:
            raise CRFAPIError(response.json(), response)

        return {
            "warehouse_deleted": True,
        }

    def get_warehouse(self, warehouse_id: str) -> Warehouse:
        """Get a warehouse"""
        response = requests.get(
            f"{self.base_url}/api/v1/projects/{warehouse_id}/",
            headers=self._get_headers(),
        )
        response.raise_for_status()
        data = response.json()
        return Warehouse(
            base_url=self.base_url,
            token=self.token,
            id=data.get("id"),
            name=data.get("name"),
            **{k: v for k, v in data.items() if k not in ["id", "name"]},
        )

    def get_table_data(
        self,
        project_id: str,
        table_id: Optional[str] = None,
        table_name: Optional[str] = None,
        offset: int = 0,
        limit: int = 10000,
        remove_embeddings: bool = True,
        chunk_id: Optional[str] = None,
        document_id: Optional[str] = None,
    ) -> list[dict]:
        """
        DEPRECATED: Use warehouse.table.get_data() instead.
        """
        raise DeprecationWarning(
            "This method is deprecated. Please use warehouse.table.get_data() instead."
        )

    def get_table_data_by_chunk(
        self,
        project_id: str,
        chunk_id: str,
        remove_embeddings: bool = True,
        offset: int = 0,
        limit: int = 10000,
    ) -> list[dict]:
        """Convenience method to get table data filtered by chunk ID"""
        raise DeprecationWarning(
            "This method is deprecated. Please use warehouse.table.get_data(chunk_id=chunk_id) instead."
        )

    def get_table_data_by_document(
        self,
        project_id: str,
        document_id: str,
        remove_embeddings: bool = True,
        offset: int = 0,
        limit: int = 10000,
    ) -> list[dict]:
        """Convenience method to get table data filtered by document ID"""
        raise DeprecationWarning(
            "This method is deprecated. Please use warehouse.table.get_data(document_id=document_id) instead."
        )

    def write_table_data(
        self, project_id: str, table_name: str, data: list[dict], override: bool = False
    ) -> dict:
        if isinstance(data, dict):
            data = [data]
        if isinstance(data, list):
            data = json.dumps(data)
        return requests.post(
            f"{self.base_url}/api/v1/projects/{project_id}/write-data/",
            headers=self._get_headers(),
            json={"table_name": table_name, "data": data, "override": override},
        )

    def get_pipeline_runs(self, project_id: str) -> list[dict]:
        return self._get_paginated_data(
            f"{self.base_url}/api/v1/projects/{project_id}/pipeline-runs"
        )

    def get_pipeline_run(self, project_id: str, pipeline_run_id: str) -> dict:
        return requests.get(
            f"{self.base_url}/api/v1/projects/{project_id}/pipeline-runs/{pipeline_run_id}",
            headers=self._get_headers(),
        )

    def abort_pipeline_run(self, project_id: str, pipeline_run_id: str) -> dict:
        return requests.post(
            f"{self.base_url}/api/v1/projects/{project_id}/pipeline-runs/{pipeline_run_id}/abort",
            headers=self._get_headers(),
        )

    def build_table(
        self,
        project_id: str,
        table_name: str,
        pipeline_name: str = "v0",
        mode: str = "recreate",
        document_ids: list[str] = None,
        llm_model: Optional[str] = None,
    ) -> dict:
        """
        Build a table with the specified parameters.

        Args:
            project_id: The ID of the project
            table_name: Name of the table to build
            pipeline_name: Name of the pipeline to use (default: "v0")
            mode: Build mode - "recreate" or other modes (default: "recreate")
            document_ids: Optional list of document IDs to process
            llm_model: Optional LLM model to use

        Returns:
            API response as dictionary

        """
        payload = {
            "table_name": table_name,
            "pipeline_name": pipeline_name,
            "mode": mode,
        }

        if document_ids:
            payload["document_ids"] = document_ids
        if llm_model:
            payload["llm_model"] = llm_model

        return requests.post(
            f"{self.base_url}/api/v1/projects/{project_id}/build-table/",
            headers=self._get_headers(),
            json=payload,
        ).json()

    def bulk_upload_documents(
        self,
        project_id: str,
        files_paths: list[str],
        skip_parsing: bool = False,
        batch_size: int = 10,
    ) -> list[dict]:
        responses = []
        data = {"skip_parsing": "true"} if skip_parsing else {}

        # Process files in batches
        for i in range(0, len(files_paths), batch_size):
            batch = files_paths[i : i + batch_size]
            files_to_upload = []

            try:
                # Open files for current batch
                for file_path in batch:
                    files_to_upload.append(
                        ("files", (file_path.split("/")[-1], open(file_path, "rb")))
                    )

                # Upload current batch
                response = requests.post(
                    f"{self.base_url}/api/v1/projects/{project_id}/documents/bulk-upload/",
                    headers=self._get_headers_without_content_type(),
                    files=files_to_upload,
                    data=data,
                )
                response.raise_for_status()
                responses.append(response.json())

            finally:
                # Ensure files are closed even if an error occurs
                for _, (_, file_obj) in files_to_upload:
                    file_obj.close()

        return responses

    def list_tables(self, project_id: str) -> list[dict]:
        return self._get_paginated_data(f"{self.base_url}/api/v1/projects/{project_id}/tables/")

    def create_table(self, project_id: str, table_name: str, columns: list[dict]) -> dict:
        return requests.post(
            f"{self.base_url}/api/v1/projects/{project_id}/tables/",
            headers=self._get_headers(),
            json={"name": table_name, "columns": columns},
        )

    def update_table(self, project_id: str, table_id: str, columns: list[dict]) -> dict:
        return requests.patch(
            f"{self.base_url}/api/v1/projects/{project_id}/tables/{table_id}/",
            headers=self._get_headers(),
            json={"columns": columns},
        )

    def create_table_version(self, project_id: str, table_id: str) -> dict:
        return requests.post(
            f"{self.base_url}/api/v1/projects/{project_id}/tables/{table_id}/versions/",
            headers=self._get_headers(),
        )

    def list_table_versions(self, project_id: str, table_id: str) -> list[dict]:
        return self._get_paginated_data(
            f"{self.base_url}/api/v1/projects/{project_id}/tables/{table_id}/versions/"
        )

    def set_deployed_table_version(self, project_id: str, table_id: str, version_id: str) -> dict:
        return requests.post(
            f"{self.base_url}/api/v1/projects/{project_id}/tables/{table_id}/set-default-version/",
            headers=self._get_headers(),
            json={"version_id": version_id},
        )

    def clear_table(self, project_id: str, table_name: str) -> dict:
        return requests.post(
            f"{self.base_url}/api/v1/projects/{project_id}/clear-table/",
            headers=self._get_headers(),
            json={"table_name": table_name},
        )

    def import_warehouse(self, zip_path: str) -> Warehouse:
        """
        Import warehouse data into a new warehouse.

        Args:
            zip_path: Path to the zip file containing warehouse export data

        Returns:
            Warehouse: The newly created warehouse object

        Raises:
            WarehouseImportError: If any critical import step fails

        """
        import_ops = ClientImportOperations(self)
        return import_ops.import_warehouse(zip_path)
