# ruff: noqa: ANN003, D105, PLW2901, RET504, PLR2004, EM102, G004, A002

from __future__ import annotations

import json
import logging
import re
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, List, Type

import requests
from datamodel_code_generator import DataModelType, InputFileType, generate
from pydantic import BaseModel

from .base import BaseAPIClient
from .exception import CRFAPIError
from .operations.warehouse_operations import WarehouseExportOperations
from .playground_agent import PlaygroundAgent
from .table import Table
from .task import Task

if TYPE_CHECKING:
    from .knowledge_assistant import KnowledgeAssistant

logger = logging.getLogger(__name__)


def inject_docstring(code: str, class_name: str, docstring: str) -> str:
    """Insert a docstring into a generated class definition."""
    docstring_block = '    """' + docstring.strip().replace("\n", "\n    ") + '"""\n'

    # Use regex to find the class definition
    pattern = rf"(class {re.escape(class_name)}\(.*?\):\n)"

    # Inject the docstring after the class declaration
    return re.sub(pattern, r"\1" + docstring_block, code)


def model_to_code(model_cls: Type[BaseModel], *, class_name: str | None = None) -> str:
    """
    Convert a Pydantic model class into nicely-formatted source code.

    using `datamodel-code-generator` entirely in memory.

    Parameters
    ----------
    model_cls : Type[BaseModel]
        The Pydantic model you want to export.
    class_name : str | None
        Optional new name for the top-level class in the generated file.

    Returns
    -------
    str
        A Python module (including imports) as plain text.

    """
    # 1) Serialize the model`s *schema* (not an instance) to JSON text
    schema_text = json.dumps(model_cls.model_json_schema())
    docstring = model_cls.__doc__ or ""

    # 2) Create a temporary *.py* file, have `generate()` write into it, read it back
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "model.py"
        generate(
            schema_text,
            input_file_type=InputFileType.JsonSchema,
            input_filename=f"{model_cls.__name__}.json",
            output=out_path,
            output_model_type=DataModelType.PydanticV2BaseModel,
            class_name=class_name or model_cls.__name__,
        )
        lines = out_path.read_text().splitlines()
        new_text = "\n".join(lines[6:])

        # Inject docstrings for all referenced models
        for _, model in model_cls.model_fields.items():  # noqa: PERF102
            if hasattr(model.annotation, "__origin__") and model.annotation.__origin__ is list:
                # Handle List[Model] case
                inner_type = model.annotation.__args__[0]
                if issubclass(inner_type, BaseModel) and inner_type.__doc__:
                    new_text = inject_docstring(new_text, inner_type.__name__, inner_type.__doc__)
            elif (
                isinstance(model.annotation, type)
                and issubclass(model.annotation, BaseModel)
                and model.annotation.__doc__
            ):
                # Handle direct Model reference case
                new_text = inject_docstring(
                    new_text, model.annotation.__name__, model.annotation.__doc__
                )

        # Finally inject the main model's docstring
        return inject_docstring(new_text, class_name or model_cls.__name__, docstring)


class Warehouse(BaseAPIClient):
    def __init__(self, base_url: str, token: str, id: str, name: str = None, **kwargs):
        super().__init__(base_url, token)
        self.name = name
        self.id = id
        # Store any additional warehouse attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _get_headers(self):
        return {"Authorization": f"Token {self.token}", "Content-Type": "application/json"}

    def _get_headers_without_content_type(self):
        return {"Authorization": f"Token {self.token}"}

    def _get_paginated_data(self, url: str, params: dict = {}) -> list[dict]:
        next_url = url
        data = []
        use_https = url.startswith("https://")
        is_first_call = True

        while next_url:
            # Ensure HTTPS consistency if base URL uses HTTPS
            if use_https and next_url.startswith("http://"):
                next_url = next_url.replace("http://", "https://")
            if is_first_call:
                response = requests.get(next_url, headers=self._get_headers(), params=params)
                is_first_call = False
            else:
                response = requests.get(next_url, headers=self._get_headers())
            response_data = response.json()
            data.extend(response_data["results"])
            next_url = response_data.get("next")

        return data

    # Table-related methods that return Table objects
    def get_table(self, table_identifier: str | int) -> Table:
        """Get a specific table by name or ID and return as Table object"""
        # First try to find by name, then by ID
        tables = self.list_tables()

        for table in tables:
            if table_identifier in (table.name, table.table_id):
                return table

        msg = f"Table '{table_identifier}' not found in warehouse {self.id}"
        raise ValueError(msg)

    def get_deployed_or_latest_chunks_table_version_id(self) -> str | None:
        """Get the deployed or latest chunks table version"""
        try:
            chunks_table = self.get_table("chunks")
        except ValueError:
            return None
        versions = chunks_table.list_versions()
        if len(versions) == 0:
            return None
        for version in versions:
            if version.get("deployed"):
                return version.get("id")
        return versions[-1].get("id")

    def create_table(
        self,
        table_name: str,
        columns: list[dict],
        object_type: str = "custom",
        object_metadata: dict = {},
        table_version_dependencies: dict = {},
    ) -> Table:
        """Create a table in this warehouse and return as Table object"""
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/tables/",
            headers=self._get_headers(),
            json={
                "name": table_name,
                "columns": columns,
                "object_type": object_type,
                "object_metadata": object_metadata,
                "table_version_dependencies": table_version_dependencies,
            },
        )
        data = response.json()

        return Table(
            base_url=self.base_url,
            token=self.token,
            warehouse_id=self.id,
            table_id=data.get("id"),
            name=data.get("name"),
            **{k: v for k, v in data.items() if k not in ["id", "name"]},
        )

    def list_tables(self) -> List[Table]:
        """List all tables in this warehouse as Table objects"""
        tables_data = self._get_paginated_data(f"{self.base_url}/api/v1/projects/{self.id}/tables/")
        tables = []
        for table_data in tables_data:
            table = Table(
                base_url=self.base_url,
                token=self.token,
                warehouse_id=self.id,
                table_id=table_data.get("id"),
                name=table_data.get("name"),
                **{k: v for k, v in table_data.items() if k not in ["id", "name"]},
            )
            tables.append(table)
        return tables

    def delete_table(self, table_identifier: str | Table) -> dict:
        """Delete a table by ID, name, or Table object"""
        if isinstance(table_identifier, Table):
            table_id = table_identifier.table_id
        else:
            # Find table by name or ID
            tables = self.list_tables()
            table_id = None
            for table in tables:
                if table_identifier in (table.name, table.table_id):
                    table_id = table.table_id
                    break

            if not table_id:
                msg = f"Table '{table_identifier}' not found in warehouse {self.id}"
                raise ValueError(msg)

        response = requests.delete(
            f"{self.base_url}/api/v1/projects/{self.id}/tables/{table_id}/",
            headers=self._get_headers(),
        )
        return response.json()

    # Tools management
    def list_tools(self) -> List[dict]:
        """List all tools in this warehouse"""
        return self._get_paginated_data(f"{self.base_url}/api/v1/projects/{self.id}/tools/")

    def create_tool(self, tool: dict) -> dict:
        """Create a tool in this warehouse"""
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/tools/",
            headers=self._get_headers(),
            json=tool,
        )
        if response.status_code != 201:
            raise CRFAPIError(response.json(), response)
        return response.json()

    def update_tool(self, tool_id: str, tool: dict) -> dict:
        """Update a tool by ID"""
        response = requests.put(
            f"{self.base_url}/api/v1/projects/{self.id}/tools/{tool_id}/",
            headers=self._get_headers(),
            json=tool,
        )
        if response.status_code != 200:
            raise CRFAPIError(response.json(), response)
        return response.json()

    def delete_tool(self, tool_id: str) -> None:
        """Delete a tool by ID"""
        response = requests.delete(
            f"{self.base_url}/api/v1/projects/{self.id}/tools/{tool_id}/",
            headers=self._get_headers(),
        )
        if response.status_code != 204:
            raise CRFAPIError(response.json(), response)

    # Agent Settings management
    def list_agent_settings(self) -> List[dict]:
        """List all agent settings in this warehouse."""
        url = f"{self.base_url}/api/v1/projects/{self.id}/agent-settings/"
        return self._get_paginated_data(url)

    def get_agent_settings(self, settings_id: str) -> dict:
        """Get agent settings by ID."""
        response = requests.get(
            f"{self.base_url}/api/v1/projects/{self.id}/agent-settings/{settings_id}/",
            headers=self._get_headers(),
        )
        if response.status_code != 200:
            raise CRFAPIError(response.json(), response)
        return response.json()

    def get_playground_agent(self, agent_settings_id: str) -> PlaygroundAgent:
        """Get a playground agent by agent settings ID and return as PlaygroundAgent object"""
        # Verify the agent settings exists
        agent_settings = self.get_agent_settings(agent_settings_id)

        return PlaygroundAgent(
            base_url=self.base_url,
            token=self.token,
            warehouse_id=self.id,
            agent_settings_id=agent_settings_id,
            **{k: v for k, v in agent_settings.items() if k not in ["id"]},
        )

    def create_agent_settings(self, settings: dict) -> dict:
        """Create agent settings in this warehouse."""
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/agent-settings/",
            headers=self._get_headers(),
            json=settings,
        )
        if response.status_code != 201:
            raise CRFAPIError(response.json(), response)
        return response.json()

    def update_agent_settings(self, settings_id: str, settings: dict) -> dict:
        """Update agent settings by ID."""
        response = requests.put(
            f"{self.base_url}/api/v1/projects/{self.id}/agent-settings/{settings_id}/",
            headers=self._get_headers(),
            json=settings,
        )
        if response.status_code != 200:
            raise CRFAPIError(response.json(), response)
        return response.json()

    def delete_agent_settings(self, settings_id: str) -> None:
        """Delete agent settings by ID."""
        response = requests.delete(
            f"{self.base_url}/api/v1/projects/{self.id}/agent-settings/{settings_id}/",
            headers=self._get_headers(),
        )
        if response.status_code != 204:
            raise CRFAPIError(response.json(), response)

    # Settings management
    def update_settings(self, **settings) -> dict:
        """Update warehouse settings"""
        response = requests.patch(
            f"{self.base_url}/api/v1/projects/{self.id}/",
            headers=self._get_headers(),
            json=settings,
        )
        return response.json()

    # Document management methods
    def upload_documents(
        self, file_paths: List[str], skip_parsing: bool = False, batch_size: int = 10
    ) -> List[dict]:
        """Upload documents to this warehouse"""
        responses = []
        data = {"skip_parsing": "true"} if skip_parsing else {}

        # Process files in batches
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i : i + batch_size]
            files_to_upload = []

            try:
                # Open files for current batch
                for file_path in batch:
                    files_to_upload.append(
                        ("files", (file_path.split("/")[-1], open(file_path, "rb")))
                    )

                # Upload current batch
                response = requests.post(
                    f"{self.base_url}/api/v1/projects/{self.id}/documents/bulk-upload/",
                    headers=self._get_headers_without_content_type(),
                    files=files_to_upload,
                    data=data,
                )
                responses.append(response.json())

            finally:
                # Ensure files are closed even if an error occurs
                for _, (_, file_obj) in files_to_upload:
                    file_obj.close()

        return responses

    def list_documents(self) -> List[dict]:
        """List all documents in this warehouse"""
        return self._get_paginated_data(f"{self.base_url}/api/v1/projects/{self.id}/documents/")

    def list_documents_without_file(self) -> List[dict]:
        """List all documents in this warehouse"""
        return self._get_paginated_data(
            f"{self.base_url}/api/v1/projects/{self.id}/documents/get-without-file/?limit=1000"
        )

    def delete_documents(self, document_ids: List[str]) -> dict:
        """Remove documents from this warehouse"""
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/documents/bulk-delete/",
            headers=self._get_headers(),
            json={"document_ids": document_ids},
        )
        return response.json()

    def create_objects_table(
        self, table_name, object_class, object_name=None, table_version_dependencies: dict = {}
    ):
        data = {
            "name": table_name,
            "columns": [
                {"name": "id", "type": "uuid"},
                {"name": "chunk_id", "type": "uuid"},
                {"name": "json_object", "type": "json"},
                {"name": "object_bbox", "type": "json"},
            ],
            "object_type": "object",
            "object_metadata": {
                "object_name": object_class.__name__ if object_name is None else object_name,
                "object_pydantic_class": model_to_code(object_class)
                if isinstance(object_class, type)
                else object_class,
            },
        }
        if table_version_dependencies.get("chunks"):
            data["table_version_dependencies"] = table_version_dependencies
        else:
            data["table_version_dependencies"] = {
                "chunks": self.get_deployed_or_latest_chunks_table_version_id()
            }

        r = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/tables/",
            headers=self._get_headers(),
            json=data,
        )
        if r.status_code == 400:
            raise CRFAPIError(f"Bad request: {r.text}", r)
        r.raise_for_status()
        data = r.json()

        return Table(
            base_url=self.base_url,
            token=self.token,
            warehouse_id=self.id,
            table_id=data.get("id"),
            name=data.get("name"),
            object_type=data.get("object_type"),
        )

    def create_tag_table(self, table_name, tagging_tree, table_version_dependencies: dict = {}):
        data = {
            "name": table_name,
            "columns": [
                {"name": "chunk_id", "type": "uuid"},
                {"name": "metadata", "type": "json"},
                {"name": "id", "type": "text"},
            ],
            "object_type": "tag",
            "object_metadata": {
                "tag_name": tagging_tree.get("name", "Manually Created Tag"),
                "tagging_tree": tagging_tree,
            },
        }
        if table_version_dependencies.get("chunks"):
            data["table_version_dependencies"] = table_version_dependencies
        else:
            data["table_version_dependencies"] = {
                "chunks": self.get_deployed_or_latest_chunks_table_version_id()
            }

        r = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/tables/",
            headers=self._get_headers(),
            json=data,
        )
        if r.status_code == 400:
            raise CRFAPIError(f"Bad request: {r.text}", r)
        r.raise_for_status()
        data = r.json()

        return Table(
            base_url=self.base_url,
            token=self.token,
            warehouse_id=self.id,
            table_id=data.get("id"),
            name=data.get("name"),
            object_type=data.get("object_type"),
        )

    def __repr__(self):
        return f"Warehouse(id='{self.id}', name='{self.name}')"

    def __str__(self):
        return f"Warehouse: {self.name} ({self.id})"

    def retrieve_with_semantic_search(
        self,
        query: str,
        n_objects: int = 10,
        indexes: list[str] = [],
        enrich_with_chunks: bool = False,
        included_tags: list[dict] | None = None,
        excluded_tags: list[dict] | None = None,
        reformulate_query: bool = False,
        rerank: bool = False,
        included_objects: list[dict] | None = None,
        excluded_objects: list[dict] | None = None,
        selected_documents: list[dict] | None = None,
    ) -> list:
        if not indexes:
            indexes = ["chunks"]
        if included_tags is None:
            included_tags = []
        if excluded_tags is None:
            excluded_tags = []
        """Retrieve objects from this warehouse with semantic search"""
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/retrieve-with-naive/",
            headers=self._get_headers(),
            json={
                "query": query,
                "n_objects": n_objects,
                "indexes": indexes,
                "enrich_with_chunks": enrich_with_chunks,
                "included_tags": included_tags,
                "excluded_tags": excluded_tags,
                "reformulate_query": reformulate_query,
                "rerank": rerank,
                "included_objects": included_objects,
                "excluded_objects": excluded_objects,
                "selected_documents": selected_documents,
            },
        )

        if response.status_code == 200:
            return response.json()["retrieval_results"]
        logger.error(f"Failed to retrieve with semantic search: {response.text}")
        return []

    def generate_answer_with_semantic_search(
        self,
        question: str,
        query: str | None,
        n_objects: int = 10,
        indexes: list[str] = [],
        enrich_with_chunks: bool = False,
        included_tags: list[dict] | None = None,
        excluded_tags: list[dict] | None = None,
        reformulate_query: bool = False,
        rerank: bool = False,
    ) -> str | None:
        if not indexes:
            indexes = ["chunks"]
        if included_tags is None:
            included_tags = []
        if excluded_tags is None:
            excluded_tags = []
        if query is None:
            query = question
        """Retrieve objects from this warehouse with semantic search"""
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/retrieve-with-naive/",
            headers=self._get_headers(),
            json={
                "query": query,
                "question": question,
                "n_objects": n_objects,
                "indexes": indexes,
                "enrich_with_chunks": enrich_with_chunks,
                "included_tags": included_tags,
                "excluded_tags": excluded_tags,
                "reformulate_query": reformulate_query,
                "rerank": rerank,
            },
        )

        if response.status_code == 200:
            return response.json()["answer"]
        logger.error(f"Failed to generate answer with semantic search: {response.text}")
        return None

    def retrieve_with_full_text_search(
        self,
        query: str,
        indexes: list[str] = [],
        n_objects: int = 10,
        enrich_with_chunks: bool = False,
        question: str = "",
        included_tags: list[dict] | None = None,
        excluded_tags: list[dict] | None = None,
        reformulate_query: bool = False,
        rerank: bool = False,
        included_objects: list[dict] | None = None,
        excluded_objects: list[dict] | None = None,
        selected_documents: list[dict] | None = None,
    ) -> list:
        """Retrieve objects from this warehouse with full-text search"""
        if not indexes:
            indexes = ["chunks"]
        if included_tags is None:
            included_tags = []
        if excluded_tags is None:
            excluded_tags = []
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/retrieve-with-full-text-search/",
            headers=self._get_headers(),
            json={
                "query": query,
                "indexes": indexes,
                "n_objects": n_objects,
                "enrich_with_chunks": enrich_with_chunks,
                "question": question,
                "included_tags": included_tags,
                "excluded_tags": excluded_tags,
                "reformulate_query": reformulate_query,
                "rerank": rerank,
                "included_objects": included_objects,
                "excluded_objects": excluded_objects,
                "selected_documents": selected_documents,
            },
        )

        if response.status_code == 200:
            return response.json()["retrieval_results"]
        logger.error(f"Failed to retrieve with full-text search: {response.text}")
        return []

    def generate_answer_with_full_text_search(
        self,
        question: str,
        query: str | None,
        indexes: list[str] = [],
        n_objects: int = 10,
        enrich_with_chunks: bool = False,
        included_tags: list[dict] | None = None,
        excluded_tags: list[dict] | None = None,
        reformulate_query: bool = False,
        rerank: bool = False,
    ) -> str | None:
        """Retrieve objects from this warehouse with full-text search"""
        if not indexes:
            indexes = ["chunks"]
        if included_tags is None:
            included_tags = []
        if excluded_tags is None:
            excluded_tags = []
        if query is None:
            query = question
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/retrieve-with-full-text-search/",
            headers=self._get_headers(),
            json={
                "query": query,
                "indexes": indexes,
                "n_objects": n_objects,
                "enrich_with_chunks": enrich_with_chunks,
                "question": question,
                "included_tags": included_tags,
                "excluded_tags": excluded_tags,
                "reformulate_query": reformulate_query,
                "rerank": rerank,
            },
        )

        if response.status_code == 200:
            return response.json()["answer"]
        logger.error(f"Failed to generate answer with full-text search: {response.text}")
        return None

    def retrieve_with_hybrid_search(
        self,
        query: str,
        indexes: list[str] = [],
        n_objects: int = 10,
        enrich_with_chunks: bool = False,
        question: str = "",
        rrf_k: int = 60,
        included_tags: list[dict] | None = None,
        excluded_tags: list[dict] | None = None,
        reformulate_query: bool = False,
        rerank: bool = False,
        included_objects: list[dict] | None = None,
        excluded_objects: list[dict] | None = None,
        selected_documents: list[dict] | None = None,
    ) -> list:
        """Retrieve objects from this warehouse with hybrid search using RRF algorithm."""
        if not indexes:
            indexes = ["chunks"]
        if included_tags is None:
            included_tags = []
        if excluded_tags is None:
            excluded_tags = []
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/retrieve-with-hybrid-search/",
            headers=self._get_headers(),
            json={
                "query": query,
                "indexes": indexes,
                "n_objects": n_objects,
                "enrich_with_chunks": enrich_with_chunks,
                "question": question,
                "rrf_k": rrf_k,
                "included_tags": included_tags,
                "excluded_tags": excluded_tags,
                "reformulate_query": reformulate_query,
                "rerank": rerank,
                "included_objects": included_objects,
                "excluded_objects": excluded_objects,
                "selected_documents": selected_documents,
            },
        )

        if response.status_code == 200:
            return response.json()["retrieval_results"]
        logger.error(f"Failed to retrieve with hybrid search: {response.text}")
        return []

    def generate_answer_with_hybrid_search(
        self,
        question: str,
        query: str | None,
        indexes: list[str] = [],
        n_objects: int = 10,
        enrich_with_chunks: bool = False,
        rrf_k: int = 60,
        included_tags: list[dict] | None = None,
        excluded_tags: list[dict] | None = None,
        reformulate_query: bool = False,
        rerank: bool = False,
    ) -> str | None:
        """Retrieve objects from this warehouse with hybrid search using RRF algorithm."""
        if not indexes:
            indexes = ["chunks"]
        if included_tags is None:
            included_tags = []
        if excluded_tags is None:
            excluded_tags = []
        if query is None:
            query = question
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/retrieve-with-hybrid-search/",
            headers=self._get_headers(),
            json={
                "query": query,
                "indexes": indexes,
                "n_objects": n_objects,
                "enrich_with_chunks": enrich_with_chunks,
                "question": question,
                "rrf_k": rrf_k,
                "included_tags": included_tags,
                "excluded_tags": excluded_tags,
                "reformulate_query": reformulate_query,
                "rerank": rerank,
            },
        )

        if response.status_code == 200:
            return response.json()["answer"]
        logger.error(f"Failed to generate answer with hybrid search: {response.text}")
        return None

    def retrieve_with_cypher(self, cypher_query: str) -> list[dict]:
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/run-neo4j-query/",
            headers=self._get_headers(),
            json={"cypher_query": cypher_query},
        )
        return response.json()

    def retrieve_with_templated_query(
        self, query_template: str, template_variables: dict, enrich_with_chunks: bool = False
    ) -> list[dict]:
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/run-templated-neo4j-query/",
            headers=self._get_headers(),
            json={
                "query_template": query_template,
                "template_variables": template_variables,
                "enrich_with_chunks": enrich_with_chunks,
            },
        )
        return response.json()

    def generate_cypher_query(self, instruction: str) -> str:
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/generate-cypher-query/",
            headers=self._get_headers(),
            json={"user_instruction": instruction},
        )
        return response.json()

    # Task-related methods that return Task objects
    def list_tasks(self) -> List[Task]:
        """List all tasks in this warehouse as Task objects"""
        tasks_data = self._get_paginated_data(
            f"{self.base_url}/api/v1/projects/{self.id}/pipeline-runs/"
        )
        tasks = []
        for task_data in tasks_data:
            task = Task(
                base_url=self.base_url,
                token=self.token,
                warehouse_id=self.id,
                task_id=task_data.get("id"),
                name=task_data.get("name"),
                **{k: v for k, v in task_data.items() if k not in ["id", "name"]},
            )
            tasks.append(task)
        return tasks

    def get_task(self, task_id: str | int) -> Task:
        """Get a specific task by ID and return as Task object"""
        response = requests.get(
            f"{self.base_url}/api/v1/projects/{self.id}/pipeline-runs/{task_id}/",
            headers=self._get_headers(),
        )
        if response.status_code != 200:
            raise CRFAPIError(response.json(), response)
        return Task(
            base_url=self.base_url,
            token=self.token,
            warehouse_id=self.id,
            task_id=response.json().get("id"),
            name=response.json().get("name"),
            **{k: v for k, v in response.json().items() if k not in ["id", "name"]},
        )

    def run_object_extraction_task(
        self,
        object_extractor_id: str,
        mode: str = "recreate-all",
        compute_alerts: bool = False,
        llm_model: str | None = None,
        document_ids: List[str] | None = None,
        chunk_ids: List[str] | None = None,
        filtering_tag_extractor_id: str | None = None,
        filtering_key: str | None = None,
        filtering_value: str | None = None,
        version_id: str | None = None,
        chunks_table_version_id: str | None = None,
        **kwargs,
    ) -> Task:
        """Run an object extraction task and return as Task object"""
        if chunk_ids is None:
            chunk_ids = []
        if document_ids is None:
            document_ids = []
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/object-extractors/{object_extractor_id}/run-push/",
            headers=self._get_headers(),
            json={
                "mode": mode,
                "compute_alerts": compute_alerts,
                "llm_model": llm_model,
                "document_ids": document_ids,
                "chunk_ids": chunk_ids,
                "filtering_tag_extractor": filtering_tag_extractor_id,
                "filtering_key": filtering_key,
                "filtering_value": filtering_value,
                "version_id": version_id,
                "chunks_table_version_id": chunks_table_version_id,
                **kwargs,
            },
        )
        if response.status_code != 200:
            raise CRFAPIError(response.json(), response)
        data = response.json()

        return Task(
            base_url=self.base_url,
            token=self.token,
            warehouse_id=self.id,
            task_id=data.get("pipeline_run_id"),
            status="pending",
            **{k: v for k, v in data.items() if k not in ["pipeline_run_id"]},
        )

    def run_tag_extraction_task(
        self,
        tag_extractor_id: str,
        mode: str = "recreate-all",
        compute_alerts: bool = False,
        llm_model: str | None = None,
        document_ids: List[str] | None = None,
        chunk_ids: List[str] | None = None,
        version_id: str | None = None,
        chunks_table_version_id: str | None = None,
        **kwargs,
    ) -> Task:
        """Run a tag extraction task and return as Task object"""
        if chunk_ids is None:
            chunk_ids = []
        if document_ids is None:
            document_ids = []
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/tag-extractors/{tag_extractor_id}/run-push/",
            headers=self._get_headers(),
            json={
                "mode": mode,
                "compute_alerts": compute_alerts,
                "llm_model": llm_model,
                "document_ids": document_ids,
                "chunk_ids": chunk_ids,
                "version_id": version_id,
                "chunks_table_version_id": chunks_table_version_id,
                **kwargs,
            },
        )
        if response.status_code != 200:
            raise CRFAPIError(response.json(), response)
        data = response.json()

        return Task(
            base_url=self.base_url,
            token=self.token,
            warehouse_id=self.id,
            task_id=data.get("pipeline_run_id"),
            status="pending",
            **{k: v for k, v in data.items() if k not in ["pipeline_run_id"]},
        )

    def run_parsing_chunking_task(
        self,
        mode: str = "recreate-all",
        document_ids: List[str] | None = None,
        chunk_ids: List[str] | None = None,
        **kwargs,
    ) -> Task:
        """Run a parsing and chunking task and return as Task object"""
        if chunk_ids is None:
            chunk_ids = []
        if document_ids is None:
            document_ids = []
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/build-table/",
            headers=self._get_headers(),
            json={
                "table_name": "pushed_chunks",
                "pipeline_name": "parsing_and_chunking",
                "mode": mode,
                "document_ids": document_ids,
                "chunk_ids": chunk_ids,
                **kwargs,
            },
        )
        response.raise_for_status()
        data = response.json()

        return Task(
            base_url=self.base_url,
            token=self.token,
            warehouse_id=self.id,
            task_id=data.get("pipeline_run_id"),
            status="pending",
            **{k: v for k, v in data.items() if k not in ["pipeline_run_id"]},
        )

    def run_parsing_task(
        self,
        mode: str = "recreate-all",
        document_ids: List[str] | None = None,
        **kwargs,
    ) -> Task:
        """Run a parsing task and return as Task object"""
        if document_ids is None:
            document_ids = []
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/build-table/",
            headers=self._get_headers(),
            json={
                "table_name": "blocks",
                "pipeline_name": "parsing",
                "mode": mode,
                "document_ids": document_ids,
                **kwargs,
            },
        )
        response.raise_for_status()
        data = response.json()

        return Task(
            base_url=self.base_url,
            token=self.token,
            warehouse_id=self.id,
            task_id=data.get("pipeline_run_id"),
            status="pending",
            **{k: v for k, v in data.items() if k not in ["pipeline_run_id"]},
        )

    def run_chunking_task(
        self,
        mode: str = "recreate-all",
        document_ids: List[str] | None = None,
        chunk_ids: List[str] | None = None,
        version_id: str | None = None,
        **kwargs,
    ) -> Task:
        """Run a chunking task and return as Task object"""
        if chunk_ids is None:
            chunk_ids = []
        if document_ids is None:
            document_ids = []
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/build-table/",
            headers=self._get_headers(),
            json={
                "table_name": "pushed_chunks",
                "pipeline_name": "chunking",
                "mode": mode,
                "document_ids": document_ids,
                "chunk_ids": chunk_ids,
                "version_id": version_id,
                **kwargs,
            },
        )
        if response.status_code != 200:
            raise CRFAPIError(response.json(), response)
        data = response.json()

        return Task(
            base_url=self.base_url,
            token=self.token,
            warehouse_id=self.id,
            task_id=data.get("pipeline_run_id"),
            status="pending",
            **{k: v for k, v in data.items() if k not in ["pipeline_run_id"]},
        )

    def list_object_extractors(self) -> list[dict]:
        return self._get_paginated_data(
            f"{self.base_url}/api/v1/projects/{self.id}/object-extractors/"
        )

    def create_object_extractor(
        self,
        brief: str,
        chunk_ids: list[str] | None = None,
        document_ids: list[str] | None = None,
        extractable_pydantic_class: str | None = None,
        extractable_object: BaseModel | None = None,
        extraction_prompt: str = None,
        llm_model: str = None,
        name: str = None,
        filtering_tag_extractor: str = None,
        filtering_key: str = None,
        filtering_value: str = None,
        enforce_single_tag: bool = False,
        compute_alerts: bool = True,
        chunks_table_version: str | None = None,
    ) -> dict:
        if chunk_ids is None:
            chunk_ids = []
        if document_ids is None:
            document_ids = []

        if extractable_object is not None:
            extractable_pydantic_class = model_to_code(extractable_object)

        # Create base payload
        payload = {
            "brief": brief,
            "chunk_ids": chunk_ids,
            "document_ids": document_ids,
            "extractable_pydantic_class": extractable_pydantic_class,
            "extraction_prompt": extraction_prompt,
            "llm_model": llm_model,
            "name": name,
            "prompt_generation_status": "completed",
            "compute_alerts": compute_alerts,
            "enforce_single_tag": enforce_single_tag,
            "chunks_table_version": chunks_table_version,
        }

        # Add filtering fields only if they are not None
        if filtering_tag_extractor is not None:
            payload["filtering_tag_extractor"] = filtering_tag_extractor
        if filtering_key is not None:
            payload["filtering_key"] = filtering_key
        if filtering_value is not None:
            payload["filtering_value"] = filtering_value

        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/object-extractors/",
            headers=self._get_headers(),
            json=payload,
        )
        if response.status_code != 201:
            raise CRFAPIError(response.json(), response)
        self.create_object_extractor_tables_and_versions(response.json())
        return response.json()

    def create_object_extractor_without_tables_and_versions(
        self,
        brief: str,
        chunk_ids: list[str] | None = None,
        document_ids: list[str] | None = None,
        extractable_pydantic_class: str | None = None,
        extractable_object: BaseModel | None = None,
        extraction_prompt: str = None,
        llm_model: str = None,
        name: str = None,
        filtering_tag_extractor: str = None,
        filtering_key: str = None,
        filtering_value: str = None,
        enforce_single_tag: bool = False,
        compute_alerts: bool = True,
        chunks_table_version: str | None = None,
    ) -> dict:
        if chunk_ids is None:
            chunk_ids = []
        if document_ids is None:
            document_ids = []

        if extractable_object is not None:
            extractable_pydantic_class = model_to_code(extractable_object)

        # Create base payload
        payload = {
            "brief": brief,
            "chunk_ids": chunk_ids,
            "document_ids": document_ids,
            "extractable_pydantic_class": extractable_pydantic_class,
            "extraction_prompt": extraction_prompt,
            "llm_model": llm_model,
            "name": name,
            "prompt_generation_status": "completed",
            "compute_alerts": compute_alerts,
            "enforce_single_tag": enforce_single_tag,
            "chunks_table_version": chunks_table_version,
        }

        # Add filtering fields only if they are not None
        if filtering_tag_extractor is not None:
            payload["filtering_tag_extractor"] = filtering_tag_extractor
        if filtering_key is not None:
            payload["filtering_key"] = filtering_key
        if filtering_value is not None:
            payload["filtering_value"] = filtering_value

        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/object-extractors/",
            headers=self._get_headers(),
            json=payload,
        )
        if response.status_code != 201:
            raise CRFAPIError(response.json(), response)
        return response.json()

    def update_object_extractor(
        self,
        object_extractor_id: str,
        brief: str = None,
        chunk_ids: list[str] = None,
        document_ids: list[str] = None,
        extractable_pydantic_class: str | None = None,
        extractable_object: BaseModel | None = None,
        extraction_prompt: str = None,
        llm_model: str = None,
        name: str = None,
        filtering_tag_extractor: str = None,
        filtering_key: str = None,
        filtering_value: str = None,
        deployed_extractable_pydantic_class: str = None,
        deployed_extraction_prompt: str = None,
        deployed_llm_model: str = None,
        set_latest_version_as_default: bool = True,
        chunks_table_version: str | None = None,
    ) -> dict:
        if extractable_object is not None:
            extractable_pydantic_class = model_to_code(extractable_object)

        fields = {
            "brief": brief,
            "chunk_ids": chunk_ids,
            "document_ids": document_ids,
            "extractable_pydantic_class": extractable_pydantic_class,
            "extraction_prompt": extraction_prompt,
            "llm_model": llm_model,
            "name": name,
            "filtering_tag_extractor": filtering_tag_extractor,
            "filtering_key": filtering_key,
            "filtering_value": filtering_value,
            "deployed_extractable_pydantic_class": deployed_extractable_pydantic_class,
            "deployed_extraction_prompt": deployed_extraction_prompt,
            "deployed_llm_model": deployed_llm_model,
            "set_latest_as_default": set_latest_version_as_default,
            "chunks_table_version": chunks_table_version,
        }

        payload = {k: v for k, v in fields.items() if v is not None}

        response = requests.patch(
            f"{self.base_url}/api/v1/projects/{self.id}/object-extractors/{object_extractor_id}/",
            headers=self._get_headers(),
            json=payload,
        )
        if response.status_code != 200:
            raise CRFAPIError(response.json(), response)
        return response.json()

    def delete_object_extractor(self, object_extractor_id: str) -> dict:
        response = requests.delete(
            f"{self.base_url}/api/v1/projects/{self.id}/object-extractors/{object_extractor_id}/",
            headers=self._get_headers(),
        )
        return response.text

    def create_object_extractor_tables_and_versions(self, object_extractor_data: dict) -> dict:
        object_extractor_id = object_extractor_data.get("id")
        pydantic_class = object_extractor_data.get("extractable_pydantic_class")
        responses = []
        tables_and_schemas = [
            {
                "name": f"extracted_objects_extractor_{object_extractor_id}",
                "columns": [
                    {"name": "id", "type": "uuid"},
                    {"name": "chunk_id", "type": "uuid"},
                    {"name": "json_object", "type": "json"},
                    {"name": "object_bbox", "type": "json"},
                ],
                "object_type": "object",
                "object_metadata": {
                    "pydantic_class": pydantic_class,
                    "object_name": object_extractor_data.get("name"),
                },
            },
            {
                "name": f"alerts_extractor_{object_extractor_id}",
                "columns": [
                    {"name": "id", "type": "uuid"},
                    {"name": "chunk_id", "type": "uuid"},
                    {"name": "json_alert", "type": "json"},
                    {"name": "extracted_object_id", "type": "uuid"},
                ],
                "object_type": "object_alert",
                "object_metadata": {},
            },
            {
                "name": f"pushed_objects_extractor_{object_extractor_id}",
                "columns": [
                    {"name": "status", "type": "text"},
                ],
                "object_type": "status",
                "object_metadata": {},
            },
        ]
        responses = []
        for table in tables_and_schemas:
            table = self.create_table(
                table["name"], table["columns"], table["object_type"], table["object_metadata"]
            )
            version = table.create_version()
            responses.append(version)
        return responses

    def run_object_extractor(
        self,
        object_extractor_id: str,
        document_ids: list[str] | None = None,
        chunk_ids: list[str] | None = None,
        tag_extractor_id: str = None,
        tag_filtering_key: str = None,
        tag_filtering_value: str = None,
        version_id: str | None = None,
        chunks_table_version_id: str | None = None,
    ) -> Task:
        if chunk_ids is None:
            chunk_ids = []
        if document_ids is None:
            document_ids = []
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/object-extractors/{object_extractor_id}/run/",
            headers=self._get_headers(),
            json={
                "document_ids": document_ids,
                "chunk_ids": chunk_ids,
                "filtering_tag_extractor": tag_extractor_id,
                "filtering_key": tag_filtering_key,
                "filtering_value": tag_filtering_value,
                "version_id": version_id,
                "chunks_table_version_id": chunks_table_version_id,
            },
        )
        task = Task(
            base_url=self.base_url,
            token=self.token,
            warehouse_id=self.id,
            task_id=response.json().get("pipeline_run_id"),
            status="pending",
            **{k: v for k, v in response.json().items() if k not in ["pipeline_run_id"]},
        )
        return task

    def list_tag_extractors(self) -> list[dict]:
        return self._get_paginated_data(
            f"{self.base_url}/api/v1/projects/{self.id}/tag-extractors/"
        )

    def create_tag_extractor(
        self,
        brief: str,
        chunk_ids: list[str] | None = None,
        document_ids: list[str] | None = None,
        tagging_tree: list[dict] | None = None,
        extraction_prompt: str = None,
        llm_model: str = None,
        name: str = None,
        compute_alerts: bool = True,
        enforce_single_tag: bool = False,
        chunks_table_version: str | None = None,
    ) -> dict:
        if chunk_ids is None:
            chunk_ids = []
        if document_ids is None:
            document_ids = []
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/tag-extractors/",
            headers=self._get_headers(),
            json={
                "brief": brief,
                "chunk_ids": chunk_ids,
                "document_ids": document_ids,
                "tagging_tree": tagging_tree,
                "extraction_prompt": extraction_prompt,
                "llm_model": llm_model,
                "name": name,
                "prompt_generation_status": "completed",
                "compute_alerts": compute_alerts,
                "enforce_single_tag": enforce_single_tag,
                "chunks_table_version": chunks_table_version,
            },
        )
        if response.status_code != 201:
            raise CRFAPIError(response.json(), response)
        self.create_tag_extractor_tables_and_versions(response.json())
        return response.json()

    def create_tag_extractor_without_tables_and_versions(
        self,
        brief: str,
        chunk_ids: list[str] | None = None,
        document_ids: list[str] | None = None,
        tagging_tree: list[dict] | None = None,
        extraction_prompt: str = None,
        llm_model: str = None,
        name: str = None,
        compute_alerts: bool = True,
        enforce_single_tag: bool = False,
        chunks_table_version: str | None = None,
    ) -> dict:
        if chunk_ids is None:
            chunk_ids = []
        if document_ids is None:
            document_ids = []
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/tag-extractors/",
            headers=self._get_headers(),
            json={
                "brief": brief,
                "chunk_ids": chunk_ids,
                "document_ids": document_ids,
                "tagging_tree": tagging_tree,
                "extraction_prompt": extraction_prompt,
                "llm_model": llm_model,
                "name": name,
                "prompt_generation_status": "completed",
                "compute_alerts": compute_alerts,
                "enforce_single_tag": enforce_single_tag,
                "chunks_table_version": chunks_table_version,
            },
        )
        if response.status_code != 201:
            raise CRFAPIError(response.json(), response)
        return response.json()

    def update_tag_extractor(
        self,
        tag_extractor_id: str,
        brief: str = None,
        chunk_ids: list[str] = None,
        document_ids: list[str] = None,
        tagging_tree: list[dict] = None,
        extraction_prompt: str = None,
        llm_model: str = None,
        name: str = None,
        compute_alerts: bool = True,
        deployed_tagging_tree: list[dict] = None,
        deployed_extraction_prompt: str = None,
        deployed_llm_model: str = None,
        enforce_single_tag: bool = None,
        set_latest_version_as_default: bool = True,
        chunks_table_version: str | None = None,
    ) -> dict:
        fields = {
            "brief": brief,
            "chunk_ids": chunk_ids,
            "document_ids": document_ids,
            "tagging_tree": tagging_tree,
            "extraction_prompt": extraction_prompt,
            "llm_model": llm_model,
            "name": name,
            "compute_alerts": compute_alerts,
            "deployed_tagging_tree": deployed_tagging_tree,
            "deployed_extraction_prompt": deployed_extraction_prompt,
            "deployed_llm_model": deployed_llm_model,
            "enforce_single_tag": enforce_single_tag,
            "set_latest_as_default": set_latest_version_as_default,
            "chunks_table_version": chunks_table_version,
        }
        payload = {k: v for k, v in fields.items() if v is not None}
        if compute_alerts is not None:
            payload["compute_alerts"] = compute_alerts

        response = requests.patch(
            f"{self.base_url}/api/v1/projects/{self.id}/tag-extractors/{tag_extractor_id}/",
            headers=self._get_headers(),
            json=payload,
        )
        if response.status_code != 200:
            raise CRFAPIError(response.json(), response)
        return response.json()

    def delete_tag_extractor(self, tag_extractor_id: str) -> str:
        response = requests.delete(
            f"{self.base_url}/api/v1/projects/{self.id}/tag-extractors/{tag_extractor_id}/",
            headers=self._get_headers(),
        )
        return response.text

    def run_tag_extractor(
        self,
        tag_extractor_id: str,
        document_ids: list[str] | None = None,
        chunk_ids: list[str] | None = None,
        version_id: str | None = None,
        chunks_table_version_id: str | None = None,
    ) -> Task:
        if chunk_ids is None:
            chunk_ids = []
        if document_ids is None:
            document_ids = []
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/tag-extractors/{tag_extractor_id}/run/",
            headers=self._get_headers(),
            json={
                "document_ids": document_ids,
                "chunk_ids": chunk_ids,
                "version_id": version_id,
                "chunks_table_version_id": chunks_table_version_id,
            },
        )
        task = Task(
            base_url=self.base_url,
            token=self.token,
            warehouse_id=self.id,
            task_id=response.json().get("pipeline_run_id"),
            status="pending",
            **{k: v for k, v in response.json().items() if k not in ["pipeline_run_id"]},
        )
        return task

    def create_tag_extractor_tables_and_versions(self, tag_extractor_data: dict) -> dict:
        tag_extractor_id = tag_extractor_data.get("id")
        tagging_tree = tag_extractor_data.get("tagging_tree")
        responses = []
        tables_and_schemas = [
            {
                "name": f"extracted_tags_extractor_{tag_extractor_id}",
                "columns": [
                    {"name": "chunk_id", "type": "uuid"},
                    {"name": "metadata", "type": "json"},
                    {"name": "id", "type": "text"},
                ],
                "object_type": "tag",
                "object_metadata": {
                    "tagging_tree": tagging_tree,
                },
            },
            {
                "name": f"alerts_tags_extractor_{tag_extractor_id}",
                "columns": [
                    {"name": "id", "type": "uuid"},
                    {"name": "chunk_id", "type": "uuid"},
                    {"name": "json_alert", "type": "json"},
                ],
                "object_type": "tag_alert",
                "object_metadata": {},
            },
        ]
        for table in tables_and_schemas:
            table = self.create_table(
                table["name"], table["columns"], table["object_type"], table["object_metadata"]
            )
            version = table.create_version()
            responses.append(version)
        return responses

    def list_chunk_extractors(self) -> list[dict]:
        return self._get_paginated_data(
            f"{self.base_url}/api/v1/projects/{self.id}/chunks-extractors/"
        )

    def create_chunk_extractor(
        self,
        name: str,
        document_ids: list[str],
        maximum_chunk_size: int = 10000,
        minimum_chunk_size: int = 200,
        page_as_separator: bool = False,
        title_section_separator_mode: str = "both",
        excluded_block_types: list[str] = [],
    ) -> dict:
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/chunks-extractors/",
            headers=self._get_headers(),
            json={
                "name": name,
                "document_ids": document_ids,
                "maximum_chunk_size": maximum_chunk_size,
                "minimum_chunk_size": minimum_chunk_size,
                "page_as_separator": page_as_separator,
                "title_section_separator_mode": title_section_separator_mode,
                "excluded_block_types": excluded_block_types,
            },
        )
        if response.status_code != 201:
            raise CRFAPIError(response.json(), response)
        return response.json()

    def update_chunk_extractor(
        self,
        chunk_extractor_id: str,
        name: str = None,
        document_ids: list[str] = None,
        maximum_chunk_size: int = None,
        minimum_chunk_size: int = None,
        page_as_separator: bool = None,
        title_section_separator_mode: str = None,
        excluded_block_types: list[str] = None,
        set_latest_version_as_default: bool = True,
    ) -> dict:
        fields = {
            "name": name,
            "document_ids": document_ids,
            "maximum_chunk_size": maximum_chunk_size,
            "minimum_chunk_size": minimum_chunk_size,
            "page_as_separator": page_as_separator,
            "title_section_separator_mode": title_section_separator_mode,
            "excluded_block_types": excluded_block_types,
            "set_latest_as_default": set_latest_version_as_default,
        }
        payload = {k: v for k, v in fields.items() if v is not None}
        response = requests.patch(
            f"{self.base_url}/api/v1/projects/{self.id}/chunks-extractors/{chunk_extractor_id}/",
            headers=self._get_headers(),
            json=payload,
        )
        return response.json()

    def delete_chunk_extractor(self, chunk_extractor_id: str) -> str:
        response = requests.delete(
            f"{self.base_url}/api/v1/projects/{self.id}/chunks-extractors/{chunk_extractor_id}/",
            headers=self._get_headers(),
        )
        return response.text

    def run_chunk_extractor(
        self,
        chunk_extractor_id: str,
        document_ids: list[str] | None = None,
        version_id: str | None = None,
    ) -> Task:
        if document_ids is None:
            document_ids = []
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.id}/chunks-extractors/{chunk_extractor_id}/run/",
            headers=self._get_headers(),
            json={
                "document_ids": document_ids,
                "version_id": version_id,
            },
        )
        task = Task(
            base_url=self.base_url,
            token=self.token,
            warehouse_id=self.id,
            task_id=response.json().get("pipeline_run_id"),
            status="pending",
            **{k: v for k, v in response.json().items() if k not in ["pipeline_run_id"]},
        )
        return task

    def get_knowledge_assistant(
        self,
        settings: dict | None = None,
        llm_model_id: str = "",
        tools: list[str] | None = None,
        additional_instructions: str | None = None,
        reasoning_tree_ids: list[str] | None = None,
    ) -> KnowledgeAssistant:
        from .client import CRFAPIClient
        from .knowledge_assistant import KnowledgeAssistant

        if settings:
            return KnowledgeAssistant(
                warehouse=self,
                crf_client=CRFAPIClient(
                    base_url=self.base_url,
                    token=self.token,
                ),
                settings=settings,
            )
        # Backward compatibility (before settings were introduced)
        logger.warning(
            "Using deprecated settings format. Please update to use the new settings format."
        )
        return KnowledgeAssistant(
            llm_model_id=llm_model_id,
            crf_client=CRFAPIClient(
                base_url=self.base_url,
                token=self.token,
            ),
            warehouse=self,
            tools=tools,
            additional_instructions=additional_instructions,
            reasoning_tree_ids=reasoning_tree_ids,
        )

    def export_warehouse(self, output_path: str | None = None) -> str:
        """
        Export all relevant data for this warehouse and create a zip file.

        Args:
            output_path: Optional path for the output zip file. If None, creates a file
                        named "warehouse_export_{warehouse_id}.zip" in the current directory.

        Returns:
            str: Path to the created zip file

        Raises:
            WarehouseExportError: If any export operation fails

        """
        export_ops = WarehouseExportOperations(self)
        return export_ops.export_warehouse(output_path)

    def sync_to_retrieval(self) -> None:
        # First we sync the chunks table
        chunks_table = self.get_table("chunks")
        logger.info(f"Pushing {chunks_table.name} to retrieval")
        sync_task = chunks_table.push_to_retrieval()
        task_result = sync_task.wait_for_completion()
        if task_result.get("status") != "completed":
            logger.error(f"Failed to push {chunks_table.name} to retrieval")
            return

        warehouse_tables = self.list_tables()
        for table in warehouse_tables:
            versions = table.list_versions()
            has_deployed_version = False
            for version in versions:
                if version.get("deployed"):
                    has_deployed_version = True
                    break
            if not has_deployed_version:
                logger.warning(f"No deployed version found for table {table.name}, skipping")
                continue
            if table.object_type in ["object", "tag"]:
                logger.info(f"Pushing {table.name} to retrieval")
                sync_task = table.push_to_retrieval()
                task_result = sync_task.wait_for_completion()
                if task_result.get("status") != "completed":
                    logger.error(f"Failed to push {table.name} to retrieval")
        return
