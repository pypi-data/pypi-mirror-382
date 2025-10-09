# ruff: noqa: E501, RUF001, UP007, D417, G004
from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

import tiktoken
from llama_index.core.agent.workflow import (
    AgentOutput,
    FunctionAgent,
    ToolCallResult,
)
from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI

if TYPE_CHECKING:
    from .client import CRFAPIClient
    from .tools import Tool
    from .warehouse import Warehouse

# Configure logging
logger = logging.getLogger(__name__)


def dict_to_markdown(data, depth=0):
    md_lines = []
    indent = "  " * depth
    bullet = "-" if depth == 0 else "*"

    # Add current node's name and description
    name = data.get("name", "Unnamed")
    description = data.get("description", "")
    md_lines.append(f'{indent}{bullet} "{name}"')
    if description:
        md_lines.append(f"{indent}  {description}")

    # Recurse into children if any
    md_lines.extend(dict_to_markdown(child, depth + 1) for child in data.get("children", []))

    return "\n".join(md_lines)


PROJECT_BRIEF = """
<project_brief>
You are an expert with deep knowledge about {project_name}. More specifically:
{project_brief}
</project_brief>
"""

ADDITIONAL_INSTRUCTIONS = """
<additional_instructions>
Consider the following additional instructions:

{additional_instructions}
</additional_instructions>
"""

TAG_HIERARCHIES = """
<tag_hierarchies>
Tag hierarchies that are available to you and for Knowledge Database retrieval

{tag_hierarchies}
</tag_hierarchies>
"""

KNOWLEDGE_GRAPH = """
<knowledge_graph>
Entities that are available to you and for Knowledge Database retrieval

{knowledge_graph}
</knowledge_graph>
"""


SYSTEM_PROMPT = """
<mission>
You are an expert system tasked with answering questions using the **Knowledge Warehouse**.
Your role is to provide accurate, clear, and citation-backed answers that rely exclusively on this warehouse.
{additional_instructions_prompt}
</mission>

<global_rules>
Provide answers that are:
  • **Citation-backed**  (If no results are found in the Knowledge Warehouse, explicitly state this and cite [Model Knowledge])
  • **Clear and legally accurate**
  • **Exhaustive** when explicitly requested (e.g., “all”, “complete”, “exhaustive list”)
  • **Concise** in all other cases
</global_rules>

<citation_rules>
No exceptions to those citation rules:
1. Every factual or regulatory statement needs a citation.
2. Format citations exactly as `[Reference <ID>]`.
   • Multiple sources: `[Reference <ID1>][Reference <ID2>]`
3. The ID (ID1, ID2, etc.) is a natural number (1,2,3, etc.) found in the field "id" of an item
4. If the warehouse lacks a direct source, cite `[Model Knowledge]`.
5. Place citations **inline, immediately after the sentence *or list item* they support**.
   • **For bullet/numbered lists, append the citation to *each* item, never as a block at the end.**
   • Example (partial list of mandatory label elements):
     - Name and address of the Responsible Person [Reference <ID1>]
     - Nominal content (weight/volume) [Reference <ID2>]
</citation_rules>
<citation_examples>

Example 1 — Sentence with citation
The job requires strong experience in React.js [Reference 12].

Example 2 — Bullet list with citations
Mandatory benefits include:
- Health insurance coverage [Reference 3]
- Paid vacation (25 days) [Reference 7]
- Meal vouchers [Reference 8]

Example 3 — Multiple sources in one citation
The average salary range for backend engineers is €45,000–€60,000 [Reference 4][Reference 9].

Example 4 — Missing warehouse data
The specific company size is not mentioned in the Knowledge Warehouse [Model Knowledge].

</citation_examples>
<process>
Step 1. Analyze the query
- Break the query into parts and identify key topics
- Leverage the Knowledge Schema to identify the type of *dimensions* (*dimensions* are all expert knowledge dimensions, like entities, tags, tag hierarchy, etc)
- If needed, split the query into sub-questions internally to ensure full coverage

Step 2. Gather evidence
- Reformulate the search if helpful and run multiple queries to the Knowledge Database via retrieval tools
- Retrieve slightly more data than needed, then filter for relevance
- Ensure every requested dimension is captured

Step 3. Write the answer
- Address all parts of the query explicitly
- Support every factual statement with inline citations
- Use quantitative data when available
- Apply the **Exhaustivity Rule**:
  • If the query requests “all”, “complete”, or “exhaustive list” → return the *entire* list in one response. No truncation
  • Provide only the fields requested (no additional context)
- For other queries, keep the answer **precise and concise**
</process>

<knowledge_warehouse_structure>
The **Knowledge Warehouse** is your exclusive source of truth.
It contains expert knowledge organized into two main components:

1. **Knowledge Schema** – defines the structure of the expert domain. The Knowledge Schema* is *available in this prompt* in the relevant sections
   - **Project Brief**: a short description of the warehouse’s purpose
   - **Tag Hierarchies**: trees of classification tags, used to categorize and filter knowledge, in addition to provide a way to structure the area of expertise. Can potentially be used as parameters for some tools
   - **Knowledge Graph**: a structured model of Entities and their attributes (like classes or database tables),  used to categorize and filter knowledge and to structure the area of expertise. Can potentially be used as parameters for some tools

2. **Knowledge Database** – holds the actual data. The Knowledge Database can be queried through the use of retrieval tools*
   - **Source Documents**: the original files (textual or graphical, e.g., PDFs)
   - **Chunks**: semantically consistent sections of documents, used as retrieval units
     • Each Chunk preserves its **lineage** (a traceable link back to the source document)
   - **Objects**: instances of Knowledge Graph Entities, extracted from documents
     • Each Object preserves its **lineage** (a traceable link back to the source chunk or to the source document)

You must use this Warehouse to search for information and ground all your answers.
</knowledge_warehouse_structure>

<knowledge_schema>
{project_brief_prompt}
{tag_hierarchies_prompt}
{object_graph_prompt}
</knowledge_schema>
"""


@dataclass
class Settings:
    model: str
    project_brief: bool = True
    additional_instructions: str | None = None
    tags_hierarchies_mode: str = "inject_all"
    tags_hierarchies_parameters: list[dict] = field(default_factory=list)
    knowledge_graph_mode: str = "inject_all"
    knowledge_graph_parameters: list[dict] = field(default_factory=list)
    tools: list[Tool] = field(default_factory=list)


class KnowledgeAssistant:
    """Knowledge Assistant for the Knowledge Warehouse."""

    def __init__(
        self,
        crf_client: CRFAPIClient,
        warehouse: Warehouse,
        settings: dict | None = None,
        llm_model_id: str = "",
        tools: Optional[List[str]] = None,
        additional_instructions: str | None = None,
        reasoning_tree_ids: Optional[List[str]] = None,
    ):
        """
        Initialize the Knowledge Assistant.

        Args:
            llm_model_id: The LLM model ID to use (eg: gpt-4o-mini)
            crf_client: The CRF client instance
            project_id: The Warehouse ID
            warehouse: The warehouse client api object instance of Warehouse
            tools: The tools to use (eg: [SemanticSearchOnChunksTool(), SemanticSearchOnObjectsTool(enrich_with_chunks=True)])
            additional_instructions: The additional instructions to use (eg: "Answer in a concise way, in French.") that will be added to the system prompt
            reasoning_tree_ids: The IDs of the reasoning trees to use

        """
        logger.info("Initializing Knowledge Assistant")

        # Store the CRF client
        self.crf_client = crf_client

        # Get the warehouse & project_id
        self.warehouse = warehouse
        self.project_id = self.warehouse.id
        self.project = self.warehouse

        # Handle settings with backward compatibility
        if isinstance(settings, dict):
            settings = Settings(**settings)
        else:
            settings = Settings(model=llm_model_id)
            settings.project_brief = True
            settings.additional_instructions = additional_instructions
            settings.tags_hierarchies_mode = "inject_all"
            if reasoning_tree_ids:
                settings.tags_hierarchies_mode = "select_tags"
                settings.tags_hierarchies_parameters = [{"id": t} for t in reasoning_tree_ids]
            settings.tools = tools or []

        # Store the settings
        self.settings: Settings = settings

        # Prepare the assistant prompt
        self.assistant_prompt = self.prompt_preparation()

        # Initialize the tools
        self.function_tools = self.tools_preparation(self.settings.tools or [])

        # Initialize the LLM
        self.token_counter = TokenCountingHandler(
            tokenizer=tiktoken.encoding_for_model(self.settings.model).encode
        )
        self.init_used_token()
        self.callback_manager = CallbackManager([self.token_counter])

        self.llm = OpenAI(model=self.settings.model, callback_manager=self.callback_manager)

        # Initialize the agent
        self.agent: FunctionAgent = FunctionAgent(
            name="Knowledge Assistant",
            description="A chat assistant that can answer questions about the knowledge warehouse.",
            tools=self.function_tools,
            llm=self.llm,
            system_prompt=self.assistant_prompt,
        )

        # Initializing the cache for links replacement
        self.cache_kw = []

        # Initializing the tool call history
        self.tool_call_history = []

        # Initializing the chat history
        self.chat_history = []

        logger.info("Knowledge Assistant initialization complete")

    # ===== TOOL CALL HISTORY =====
    def get_tool_call_history(self):
        """Get the tool call history."""
        return self.tool_call_history

    def log_tool_call(self, tool_name: str, params: dict, results: dict):
        """Add a tool call to the tool call history."""
        self.tool_call_history.append(
            {
                "tool_name": tool_name,
                "params": params,
                "results": results,
            }
        )

    def tools_preparation(self, tools: list[Tool]):
        """Prepare the tools for the agent. Return the LLM tools."""
        llm_tools = []
        # Initialize the tools
        for tool_index, tool in enumerate(tools):
            tool_name = f"{tool.tool_name()}_{tool_index}"
            tool.set_assistant(self)
            llm_tools.append(
                FunctionTool.from_defaults(
                    name=tool_name,
                    description=f"{tool_name}\n{tool.tool_description()}",
                    fn=tool.tool_function(),
                )
            )
        return llm_tools

    # ===== PROMPT PREPARATION =====
    def _sanitize_additional_instructions(self, value: str) -> str:
        """
        Validate and sanitize the additional instructions to prevent prompt injection attacks.

        This method enforces constraints such as:
        - Length limits
        - Strips dangerous template directives
        """
        # Handle None values
        if value is None:
            return ""

        # Strip whitespace
        value = value.strip()

        # Length validation - reasonable limit for system prompts
        max_length = 10000
        if len(value) > max_length:
            logger.info(f"System prompt is too long, truncating it to {max_length} characters")
            value = value[:max_length]

        # Remove potentially dangerous template directives that could be used for injection
        dangerous_patterns = [
            r"\{[^}]*\}",  # Remove any template-style placeholders
            r"\{\{[^}]*\}\}",  # Remove double-brace template directives
            r"\{%.*?%\}",  # Remove Jinja2-style template directives
            r"\{#.*?#\}",  # Remove Jinja2-style comments
            r"\{if.*?\}",  # Remove conditional template directives
            r"\{for.*?\}",  # Remove loop template directives
            r"\{include.*?\}",  # Remove include directives
            r"\{extends.*?\}",  # Remove extends directives
        ]

        for pattern in dangerous_patterns:
            value = re.sub(pattern, "", value, flags=re.IGNORECASE | re.DOTALL)

        # Remove any remaining curly braces that might be used for injection
        value = value.replace("{", "").replace("}", "")

        # Remove any script tags or HTML-like structures
        value = re.sub(r"<script.*?</script>", "", value, flags=re.IGNORECASE | re.DOTALL)
        value = re.sub(r"<.*?>", "", value)  # Remove any HTML tags

        # Remove any command injection patterns
        command_patterns = [
            r"`.*?`",  # Backtick command execution
            r"\$\(.*?\)",  # Command substitution
            r";.*",  # Command chaining
            r"&&.*",  # Command chaining
            r"\|\|.*",  # Command chaining
        ]

        for pattern in command_patterns:
            value = re.sub(pattern, "", value, flags=re.IGNORECASE | re.DOTALL)

        return value.strip()

    def _prepare_project_brief(self):
        """Utility function to prepare the project brief."""
        if self.settings.project_brief:
            logger.info(
                f"Preparing project brief for {self.project.name}, with brief: {self.project.business_brief}"
            )
            return PROJECT_BRIEF.format(
                project_name=self.project.name, project_brief=self.project.business_brief
            )
        return ""

    def _prepare_additional_instructions(self):
        """Utility function to prepare the additional instructions."""
        if self.settings.additional_instructions:
            sanitized_instructions = self._sanitize_additional_instructions(
                self.settings.additional_instructions
            )
            return ADDITIONAL_INSTRUCTIONS.format(additional_instructions=sanitized_instructions)
        return ""

    def _prepare_tag_hierarchies(self):
        """Utility function to prepare the tag hierarchies."""
        if self.settings.tags_hierarchies_mode in ["inject_all", "select_tags"]:
            metadata = [tag.object_metadata for tag in self.tables if tag.object_type == "tag"]
            if self.settings.tags_hierarchies_mode == "select_tags":
                filter_ids = [item["id"] for item in self.settings.tags_hierarchies_parameters]
                metadata = [tag for tag in metadata if tag["tagging_tree"]["id"] in filter_ids]
            if metadata != []:
                md = ""
                for i, tag in enumerate(metadata):
                    md += f"## Hierarchy {i + 1}: {tag['tag_name']}\n"
                    md += dict_to_markdown(tag["tagging_tree"])
                    md += "\n\n"
                return TAG_HIERARCHIES.format(tag_hierarchies=md)
        return ""

    def _prepare_object_graph(self):
        """Utility function to prepare the object graph (objects)"""
        if self.settings.knowledge_graph_mode in ["inject_all", "select_subgraph"]:
            metadata = [obj.object_metadata for obj in self.tables if obj.object_type == "object"]
            if self.settings.knowledge_graph_mode == "select_subgraph":
                filter_names = [item["name"] for item in self.settings.knowledge_graph_parameters]
                metadata = [obj for obj in metadata if obj["object_name"] in filter_names]
            if metadata != []:
                md = ""
                for i, obj in enumerate(metadata):
                    md += f"## Entity {i + 1}: {obj['object_name']}\n"
                    md += f"```python\n{obj['object_pydantic_class']}\n```"
                    md += "\n\n"
                return KNOWLEDGE_GRAPH.format(knowledge_graph=md)
        return ""

    def prompt_preparation(self):
        """Prepare the prompt by merging the different parts."""
        self.tables = []
        if self.settings.knowledge_graph_mode in [
            "inject_all",
            "select_subgraph",
        ] or self.settings.tags_hierarchies_mode in ["inject_all", "select_tags"]:
            self.tables = self.warehouse.list_tables()
            logger.info(f"Found {len(self.tables)} tables")
        return SYSTEM_PROMPT.format(
            project_brief_prompt=self._prepare_project_brief(),
            additional_instructions_prompt=self._prepare_additional_instructions(),
            tag_hierarchies_prompt=self._prepare_tag_hierarchies(),
            object_graph_prompt=self._prepare_object_graph(),
        )

    # ===== CHAT =====
    def _run_agent(self, query: str):  # noqa: C901
        # Chat with the agent (including tool calls)
        async def async_generator():
            handler = self.agent.run(query, chat_history=self.chat_history.copy())
            async for event in handler.stream_events():
                yield event

        # Create a new event loop for this generator if there is no running one
        new_loop = False
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, safe to create a new one
            new_loop = True
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            # Convert async generator to sync
            async_gen = async_generator()
            while True:
                event = loop.run_until_complete(async_gen.__anext__())
                if isinstance(event, AgentOutput):
                    # Log agent output
                    self.delta_chat_history.append(event.response)
                if isinstance(event, ToolCallResult):
                    # Log tool call result
                    message = ChatMessage(
                        role="tool",
                        content=event.tool_output.content,
                        additional_kwargs={
                            "tool_call_id": event.tool_id,
                            "name": event.tool_output.tool_name,
                        },
                    )
                    self.delta_chat_history.append(message)

        except StopAsyncIteration:
            pass
        except Exception:
            logger.exception("Error during agent execution")
        finally:
            if new_loop:
                pending_tasks = asyncio.all_tasks(loop)
                if pending_tasks:
                    try:
                        loop.run_until_complete(
                            asyncio.wait_for(
                                asyncio.gather(*pending_tasks, return_exceptions=True), timeout=3.0
                            )
                        )
                    except Exception:
                        logger.exception("Error during task cleanup")

                loop.close()
        assistant_messages = [
            message for message in self.delta_chat_history if message.role == "assistant"
        ]
        if assistant_messages:
            return assistant_messages[-1]
        return None

    async def _run_async_agent(self, query: str):
        """Async version of _run_agent that works in an async context."""
        try:
            # Chat with the agent (including tool calls)
            handler = self.agent.run(query, chat_history=self.chat_history.copy())
            async for event in handler.stream_events():
                if isinstance(event, AgentOutput):
                    # Log agent output
                    self.delta_chat_history.append(event.response)
                if isinstance(event, ToolCallResult):
                    # Log tool call result
                    message = ChatMessage(
                        role="tool",
                        content=event.tool_output.content,
                        additional_kwargs={
                            "tool_call_id": event.tool_id,
                            "name": event.tool_output.tool_name,
                        },
                    )
                    self.delta_chat_history.append(message)
        except Exception:
            logger.exception("Error during async agent execution")

        assistant_messages = [
            message for message in self.delta_chat_history if message.role == "assistant"
        ]
        if assistant_messages:
            return assistant_messages[-1]
        return None

    def chat(self, query: str):
        """Chat with the assistant."""
        self.delta_chat_history = [ChatMessage(role="user", content=query)]
        response = self._run_agent(query)
        self.chat_history.extend(self.delta_chat_history)
        content = ""
        if response:
            content = response.content if response and hasattr(response, "content") else ""
        return self.replace_findings_with_links(content)

    async def achat(self, query: str):
        """Async chat with the assistant."""
        self.delta_chat_history = [ChatMessage(role="user", content=query)]
        response = await self._run_async_agent(query)
        self.chat_history.extend(self.delta_chat_history)
        content = ""
        if response:
            content = response.content if response and hasattr(response, "content") else ""
        return self.replace_findings_with_links(content)

    # ===== TOKEN COUNTER =====

    def init_used_token(self):
        """RAZ of the used tokens counters."""
        self.input_token_count_so_far = 0
        self.output_token_count_so_far = 0

    def get_used_tokens(self):
        """Get the used tokens since the last call to this method."""
        used_tokens_input = (
            self.token_counter.prompt_llm_token_count - self.input_token_count_so_far
        )
        used_tokens_output = (
            self.token_counter.completion_llm_token_count - self.output_token_count_so_far
        )
        self.input_token_count_so_far = self.token_counter.prompt_llm_token_count
        self.output_token_count_so_far = self.token_counter.completion_llm_token_count
        return used_tokens_input, used_tokens_output

    # ===== CACHE and Reference management =====
    def store_in_cache(self, results):
        """
        Store the results in the cache.

        The cache is used to store the results tool calls.
        It is used to replace the [Reference ####] with the corresponding links.
        We use the uuid of the object, if available, to uniquely identify it and avoid duplicates.
        We add a unique "id" field to the result so that the Agent to reference the object like [Reference <ID>]
        """
        uuids = {obj["uuid"] for obj in self.cache_kw if "uuid" in obj}
        last_id = max((obj["id"] for obj in self.cache_kw), default=0)
        for result in results:
            # Do not add the same object twice (if the uuid is not present, we add the object)
            uuid = result.get("uuid")
            if uuid in uuids:
                continue
            last_id += 1
            result["id"] = last_id
            self.cache_kw.append(result)
            if uuid:
                uuids.add(uuid)

    def replace_findings_with_links(self, text: str):
        """Replace all occurrences of [Reference ####] with links."""
        try:
            # Extract all IDs from the text
            id_matches = re.findall(r"\[Reference (.+?)\]", text)
            # Replace the IDs with the corresponding links
            for current_id in id_matches:
                # Remove the < and > from the ID if any
                clean_id = current_id.strip("<>")
                result = [obj for obj in self.cache_kw if str(obj["id"]) == str(clean_id)]
                if len(result) == 0:
                    continue
                # Use the most recent result if multiple matches (data integrity issue)
                result = result[-1]
                reference_url = result.get("reference_url")
                if reference_url:
                    text = text.replace(
                        f"[Reference {current_id}]",
                        f" *[Ref {result['id']}]({reference_url})* ",
                    )
                else:
                    text = text.replace(f"[Reference {current_id}]", "")
        except Exception:
            logger.exception("Unexpected error occurred while extracting link for finding")
        return text
