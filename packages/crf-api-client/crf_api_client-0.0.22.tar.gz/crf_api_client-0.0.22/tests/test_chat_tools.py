# ruff: noqa: E501, G004, T201, S101, PLR2004
from crf_api_client.tools import SemanticSearchOnChunksTool, SemanticSearchOnObjectsTool


def test_semantic_search_on_chunks_tool(warehouse):
    """Test querying about backend engineer skills."""
    assistant = warehouse.get_knowledge_assistant(
        settings={
            "model": "gpt-4o-mini",
            "additional_instructions": "Answer in a concise way",
            "tools": [SemanticSearchOnChunksTool()],
        }
    )
    response = assistant.chat("What are the main skills of a backend engineer?")

    # Assert that we got a response
    assert response is not None
    assert len(response) > 0

    # Print response and token usage for debugging
    print(f"test_semantic_search_on_chunks_tool: Response: {response}")
    print("-*-" * 20)


def test_semantic_search_on_objects_tool(warehouse):
    """Test querying about backend engineer skills."""
    assistant = warehouse.get_knowledge_assistant(
        settings={
            "model": "gpt-4o-mini",
            "additional_instructions": "Answer in a concise way",
            "tools": [SemanticSearchOnObjectsTool()],
        }
    )
    response = assistant.chat("Skills of a backend engineer ?")

    # Assert that we got a response
    assert response is not None
    assert len(response) > 0

    # Print response and token usage for debugging
    print(f"test_semantic_search_on_objects_tool: Response: {response}")
    print("-*-" * 20)
