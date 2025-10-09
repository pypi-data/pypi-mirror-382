# ruff: noqa: RUF001
from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import tiktoken
from llama_index.core.agent.workflow import ReActAgent, AgentStream, ToolCallResult
from llama_index.core.workflow import Context
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.core.prompts import PromptTemplate

if TYPE_CHECKING:
    from .client import CRFAPIClient

# Configure logging
logger = logging.getLogger(__name__)


def dict_to_markdown(data, depth=0):
    md_lines = []
    indent = "  " * depth
    bullet = "-" if depth == 0 else "*"

    # Add current node's name and description
    name = data.get("name", "Unnamed")
    description = data.get("description", "")
    md_lines.append(f"{indent}{bullet} **{name}**")
    if description:
        md_lines.append(f"{indent}  {description}")

    # Recurse into children if any
    for child in data.get("children", []):
        md_lines.append(dict_to_markdown(child, depth + 1))

    return "\n".join(md_lines)


@dataclass
class Tag:
    id: str
    name: str
    brief: str
    tree: dict
    root_id: str = field(default="")
    tag_ids: list[tuple[str, str]] = field(default_factory=list)

    def __post_init__(self):
        self.root_id = self.tree.get("id", "")

        def _traverse_node(node: dict[str, Any]) -> None:
            """Recursively traverse tree nodes to collect tag IDs."""
            if "id" in node and node["id"] != self.root_id:
                self.tag_ids.append((self.root_id, node["id"]))

            if "children" in node and isinstance(node["children"], list):
                for child in node["children"]:
                    _traverse_node(child)

        _traverse_node(self.tree)

    def __str__(self) -> str:
        """Return a nice string representation of the tag for inclusion in prompts."""
        # Escape curly braces in JSON to prevent format string interpretation
        tree_md = dict_to_markdown(self.tree)
        return f"""Tag: {self.name} (ID: {self.id})
Description: {self.brief}
Tagging tree: 

{tree_md}
"""


@dataclass
class Object:
    id: str
    name: str
    brief: str

    def __str__(self) -> str:
        """Return a nice string representation of the object for inclusion in prompts."""
        return f"""Object: {self.name} (ID: {self.id})
Description: {self.brief}
"""


SYSTEM_PROMPT = """
You are an expert with deep knowledge about {project_brief}.

────────────────────────────────
🚨 CRITICAL: CITATION REQUIREMENTS 🚨
EVERY factual statement MUST include a citation using the exact format below:
• Format: [Reference <ID>] where <ID> is from tool results
• Example: "Lysine increases milk protein yield [Reference 0][Reference 1]"
• Use the id field from EVERY tool result you reference
• Place citations immediately after each statement they support

────────────────────────────────
MISSION  :  WHAT YOU COVER

You are tasked with answering questions in your area of expertise describe above.
You will use the **Knowledge Warehouse** to find relevant information and provide accurate,
citation-backed answers.

All answers must draw on the **Knowledge Warehouse** .
**Query the warehouse exclusively with the provided tools.**

---------------------------------------
TOOLS AND STRATEGIC USAGE

🔍 **YOU MUST USE MULTIPLE TOOLS FOR COMPREHENSIVE ANSWERS** 🔍

You have access to the following tools, each serving different purposes:

{tool_desc}

**TOOL USAGE STRATEGY:**
1. **semantic_search_on_chunks**: Use this for general content searches, broad topic exploration, and finding detailed explanations or mechanisms
2. **semantic_search_on_objects**: Use this when you need structured object data, specific entity information, or when the question relates to particular objects/entities

**MANDATORY MULTI-TOOL APPROACH:**
• **ALWAYS use BOTH tools** unless one is clearly irrelevant
• Start with one tool, analyze results, then use the other tool with refined queries
• Use multiple searches with different phrasings and angles
• Cross-validate findings between tools
• Look for complementary information from different search strategies

---------------------------------------
ORGANISATION OF KNOWLEDGE WAREHOUSE

You have access to a **Knowledge Warehouse** about {project_brief}.

────────────────────────────────
ANSWERING METHOD
1. **Analyse the query**
   • Break it into parts and detect key topics to address
   • Identify from the structure the type of dimensions and the associated values that are relevant to the query
   • Split the user query into sub-questions if needed, to ensure all dimensions - values are covered.

2. **Gather evidence (MULTI-TOOL STRATEGY)**
   • **Phase 1**: Start with semantic_search_on_chunks for broad understanding
   • **Phase 2**: Use semantic_search_on_objects for specific entity/object information
   • **Phase 3**: Conduct additional searches with refined queries based on initial findings
   • **Phase 4**: Cross-validate and fill gaps with complementary searches
   • Reformulate the search if helpful and split it into various queries to the Knowledge Warehouse
   • Use the warehouse tools to pull slightly more data than needed, then filter for relevance
   • Capture **every** requested dimension (annex, limit, condition, etc.)

3. **Write the answer**
   • Address every sub-question or implicit request
   • As much as possible, provide a quantitative answer supported by the warehouse
   • Insert citations inline (see rules above)
   • **Exhaustive-list rule:**
     – If the user's words (e.g. "all", "complete", "exhaustive list") demand exhaustivity, return
     the *entire* list in one response—no truncation, no "let me know if you need more."
     – Provide *only* the fields requested.
       • Example: "List all chemical names that benefit from exemptions for
       hair-care products" → output **just the chemical names**, one per line/bullet, each with its own citation.
  • If the user asks for a list of all the chemicals in the warehouse, return the entire list.
   • For other requests, be precise **and concise**—include only what is relevant.

---------------------------------------
OUTPUT FORMAT

Please start with the following reasoning(thought, action, action input and observation) format:
```
Thought: The user is asking about [user's question]. I need to start with semantic_search_on_chunks to get a broad understanding of the topic, then use semantic_search_on_objects for specific entity information.
Action: semantic_search_on_chunks
Action Input: the input to the tool, in a JSON format representing the kwargs. For example, "query" as a key, [user's question] as a value.
Observation: [observation from the semantic_search_on_chunks tool] <- this is a response from the tool.
Thought: Now I have some initial information. I should use semantic_search_on_objects to get more specific object/entity information related to [specific aspects from previous results].
Action: semantic_search_on_objects
Action Input: the input to the tool, in a JSON format representing the kwargs
Observation: [observation from the semantic_search_on_objects tool]
```

After these initial searches, continue with additional tool usage to ensure comprehensive coverage:
```
Thought: Based on the results so far, I need to dig deeper into [specific aspect]. I'll search for more information about [refined query based on previous findings].
Action: [tool name - choose the most appropriate tool]
Action Input: the input to the tool, in a JSON format representing the kwargs
Observation: [observation from the tool]
```

**IMPORTANT REASONING GUIDELINES:**
• Please ALWAYS start with a Thought and explain your tool strategy
• Break down complex questions into multiple searches
• Use at least 2-3 tool calls for most questions (unless very simple)
• Always justify why you're using a specific tool
• Cross-reference findings between different tool results
• Examples of good reasoning:
  ```
  Thought: I found some general information, but I need to validate this with object-specific data using semantic_search_on_objects.
  ```
  ```
  Thought: The previous searches covered the main topic, but I should search for additional details about [specific subtopic] to ensure completeness.
  ```

NEVER surround your response with markdown code markers. You may use code markers within your response if you need to.
Please use a valid JSON format for the Action Input.
If this format is used, the tool will respond in the following format:

```
Observation: tool response
```

You should keep repeating the reasoning format above until you have enough information to answer the question without using any more tools. 
**MINIMUM REQUIREMENT: Use at least 2 different tool calls before providing your final answer, unless the question is extremely simple.**

At that point, you MUST respond in one of the following two formats:

```
Thought: I can answer without using any more tools. I'll use the user's language to answer
Answer: [your answer here WITH CITATIONS using [Reference <ID>] format for EVERY factual statement]
```

```
Thought: I cannot answer the question with the provided tools.
Answer: [your answer here (In the same language as the user's question)]
```

────────────────────────────────
🚨 CITATION REMINDER 🚨
BEFORE writing your final Answer:
1. Review each factual statement in your response
2. Ensure EVERY statement has [Reference <ID>] citation
3. Use the id field from tool results (e.g., if tool returned "id": 0, cite as [Reference 0])
4. Multiple sources: [Reference 0][Reference 1]

Example of correct citation usage:
"Lysine enhances protein synthesis [Reference 0] and reduces degradation [Reference 1]. It activates mTOR pathways [Reference 0] and is limiting in corn-based diets [Reference 2]."

────────────────────────────────
CURRENT CONVERSATION

Below is the current conversation consisting of interleaving human and assistant messages:
"""


class KnowledgeWarehouseReActAssistant:
    def __init__(
        self,
        llm_model_id: str,
        crf_client: CRFAPIClient,
        project_id: str,
        included_tags: list[tuple[str, str, str]] | None = None,
        excluded_tags: list[tuple[str, str, str]] | None = None,
        default_top_k: int = 10,
        verbose: bool = True,
    ):
        logger.info(f"Initializing KnowledgeWarehouseReActAssistant with model: {llm_model_id}")

        self.token_counter = TokenCountingHandler(
            tokenizer=tiktoken.encoding_for_model(llm_model_id).encode
        )
        callback_manager = CallbackManager([self.token_counter])
        self.llm = OpenAI(model=llm_model_id)
        self.crf_client = crf_client
        self.project_id = project_id
        self.warehouse = crf_client.get_warehouse(project_id)
        self.project_brief = self.warehouse.business_brief
        self.included_tags = included_tags
        self.excluded_tags = excluded_tags
        self.verbose = verbose

        # List tags from warehouse
        try:
            # List all tags (tag extractors) available in the warehouse
            self.tags = [
                Tag(tag["id"], tag["name"], tag["brief"], tag["tagging_tree"])
                for tag in self.warehouse.list_tag_extractors()
            ]
        except Exception as e:
            logger.warning(f"Could not list tags from warehouse: {e}")
            self.tags = []

        # To simplify the call of the LLM, we map the tag pairs to triples internally
        self._tags_pairs_to_triples: dict[tuple[str, str], tuple[str, str, str]] = {
            tag_pair: (f"extracted_tags_extractor_{tag.id}", tag_pair[0], tag_pair[1])
            for tag in self.tags
            for tag_pair in tag.tag_ids
        }
        if self.included_tags is not None and not set(self.included_tags).issubset(
            set(self._tags_pairs_to_triples.values())
        ):
            invalid_tags = self.included_tags
            msg = f"Included tags {invalid_tags} are not valid. Please provide valid tag pairs."
            raise ValueError(msg)
        if self.excluded_tags is not None and not set(self.excluded_tags).issubset(
            set(self._tags_pairs_to_triples.values())
        ):
            invalid_tags = self.excluded_tags
            msg = f"Excluded tags {invalid_tags} are not valid. Please provide valid tag pairs."
            raise ValueError(msg)

        # List objects from warehouse
        try:
            self.objects = [
                Object(obj["id"], obj["name"], obj["brief"])
                for obj in self.warehouse.list_object_extractors()
            ]
        except Exception as e:
            logger.warning(f"Could not list objects from warehouse: {e}")
            self.objects = []

        self.default_top_k = default_top_k

        tools = [
            FunctionTool.from_defaults(
                fn=self._semantic_search_on_objects,
                name="semantic_search_on_objects",
            ),
            FunctionTool.from_defaults(
                fn=self._semantic_search_on_chunks,
                name="semantic_search_on_chunks",
            ),
        ]

        tag_structure = "\n\n".join([str(tag) for tag in self.tags])
        object_structure = "\n\n".join([str(obj) for obj in self.objects])

        assistant_prompt = PromptTemplate(SYSTEM_PROMPT).partial_format(
            project_brief=self.project_brief,
            tag_structure=tag_structure,
            object_structure=object_structure,
        )
        assistant_prompt_str = assistant_prompt.format()

        self.agent = ReActAgent(
            name="KnowledgeWarehouseReActAssistant",
            description="An assistant that can answer questions about the knowledge warehouse.",
            tools=tools,
            llm=self.llm,
            system_prompt=assistant_prompt_str,
            verbose=self.verbose,
            callback_manager=callback_manager,
        )
        self.agent.update_prompts({"react_header": assistant_prompt_str})
        self.tool_call_history = []
        self.cache_kw = []
        self.run_once: bool = False
        logger.info("KnowledgeWarehouseReActAssistant initialization complete")

    def add_to_cache_update_id_format_for_context(self, results):
        logger.info(f"Updating kw cache with {len(results)} new results")
        id_start = len(self.cache_kw)
        for i, result in enumerate(results):
            result["id"] = i + id_start
            self.cache_kw.append(result)
        return [
            {
                "id": result["id"],
                "type": result["labels"],
                "content": result["content"],
            }
            for result in results
        ]

    def _semantic_search_on_objects(
        self, query: str, top_k: int | None = None, enrich_with_chunks: bool = True
    ):
        """
        Perform a semantic search over objects in the knowledge warehouse, optionally enriching the results with related content chunks.

        🚨 IMPORTANT: You MUST cite every fact you use from the results using [Reference <ID>] format!

        Args:
            query (str): The search query.
            top_k (int, optional): The maximum number of objects to retrieve. Defaults to self.default_top_k if not specified.
            enrich_with_chunks (bool): Whether to include related content chunks in the results.

        Returns:
            List[dict]: A list of result dictionaries, each containing id, labels, and content keys.
                       USE THE id FIELD FOR CITATIONS: [Reference <ID>]
        """

        try:
            results = self.warehouse.retrieve_with_semantic_search(
                query,
                n_objects=top_k or self.default_top_k,
                indexes=["objects"],
                enrich_with_chunks=enrich_with_chunks,
            )
        except Exception as warehouse_error:
            logger.exception(f"Warehouse method failed: {str(warehouse_error)}")
            return []
        if isinstance(results, dict) and "retrieval_results" in results:
            results = results["retrieval_results"]
        elif not isinstance(results, list):
            logger.warning(f"Unexpected response format: {type(results)}")
            return []
        self.tool_call_history.append(
            {
                "tool_type": "semantic_search_on_objects",
                "query": query,
                "top_k": top_k,
                "results": results,
            }
        )
        return self.add_to_cache_update_id_format_for_context(results)

    def _semantic_search_on_chunks(self, query: str, top_k: int | None = None):
        """
        Perform a semantic search over content chunks in the knowledge warehouse.

        🚨 IMPORTANT: You MUST cite every fact you use from the results using [Reference <ID>] format!

        Args:
            query (str): The search query.
            top_k (int, optional): The maximum number of chunks to retrieve. Defaults to self.default_top_k if not specified.

        Returns:
            List[dict]: A list of result dictionaries, each containing id, labels, and content keys.
                       USE THE id FIELD FOR CITATIONS: [Reference <ID>]
        """
        try:
            results = self.warehouse.retrieve_with_semantic_search(
                query,
                indexes=["chunks"],
                n_objects=top_k or self.default_top_k,
            )
        except Exception as warehouse_error:
            logger.exception(f"Warehouse method failed: {str(warehouse_error)}")
            return []
        if isinstance(results, dict) and "retrieval_results" in results:
            results = results["retrieval_results"]
        elif not isinstance(results, list):
            logger.warning(f"Unexpected response format: {type(results)}")
            return []
        logger.info("Semantic search on chunks completed successfully")
        self.tool_call_history.append(
            {
                "tool_type": "semantic_search_on_chunks",
                "query": query,
                "top_k": top_k,
                "results": results,
            }
        )
        return self.add_to_cache_update_id_format_for_context(results)

    def extract_link_for_finding(self, finding_id: str):
        """Extract link for a specific finding ID."""
        try:
            referenced_objects = [obj for obj in self.cache_kw if obj["id"] == int(finding_id)]
            if len(referenced_objects) == 0:
                logger.warning(f"Finding ID {finding_id} not found in cache.")
                return ""
            if len(referenced_objects) > 1:
                logger.warning(
                    f"Multiple objects found for Finding ID {finding_id}. Using the first one."
                )

            referenced_object = referenced_objects[0]
            return referenced_object.get("reference_url", "")
        except (IndexError, ValueError) as e:
            logger.exception(f"Error extracting link for finding {finding_id}: {e!s}")
            return ""
        except Exception as e:
            logger.exception(f"Unexpected error occurred while extracting link for finding: {e}")
            return ""

    def run(self, query: str, max_iterations: int = 20):
        return asyncio.run(self.arun(query, max_iterations))

    async def arun(self, query: str, max_iterations: int = 20):
        if self.run_once:
            logger.info(
                "ReActAssistant has already run once. Please create a new instance of the ReActAssistant to run again."
            )
            return
        self.run_once = True
        context = Context(self.agent)
        handler = self.agent.run(user_msg=query, ctx=context, max_iterations=max_iterations)
        if self.verbose:
            async for event in handler.stream_events():
                if isinstance(event, ToolCallResult):
                    print(
                        f"\nCall {event.tool_name} with {event.tool_kwargs}\nReturned: {event.tool_output}"
                    )
                if isinstance(event, AgentStream):
                    print(f"{event.delta}", end="", flush=True)
        response = await handler
        return self.replace_findings_with_links(response.response.content)

    def replace_findings_with_links(self, text: str):
        """Replace all occurrences of [Reference ####] with links."""

        def replace_match(match):
            findings = match.group(0)
            # Handle both formats:
            # [Reference 1, Reference 3, Reference 4] and [References 1, 3, 4]
            if "References" in findings and findings.count("Reference") == 1:
                # Format: [References 1, 3, 4] - extract all numbers
                finding_ids = re.findall(r"\d+", findings)
            else:
                # Format: [Reference 1, Reference 3, Reference 4] - extract numbers after "Reference"
                finding_ids = re.findall(r"Reference (\d+)", findings)

            # Replace each finding number with a Link(url) format
            links = [
                rf"[\[Ref {finding_id}\]]({self.extract_link_for_finding(finding_id)})"
                for finding_id in finding_ids
            ]
            return ", ".join(links)

        # Updated regex to match both formats:
        # [Reference 1, Reference 3, Reference 4] and [References 1, 3, 4]
        pattern = r"\[References? (?:\d+(?:, (?:Reference )?\d+)*)\]"
        return re.sub(pattern, replace_match, text)
