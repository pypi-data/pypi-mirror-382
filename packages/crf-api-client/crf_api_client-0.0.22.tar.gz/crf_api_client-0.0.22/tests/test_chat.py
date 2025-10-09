# ruff: noqa: E501, G004, T201, S101, PLR2004
from crf_api_client.client import CRFAPIClient
from crf_api_client.tools import SemanticSearchOnChunksTool


def test_client_creation(api_credentials):
    """Test that client can be created with valid credentials."""
    client = CRFAPIClient(base_url=api_credentials["base_url"], token=api_credentials["token"])
    assert client is not None


def test_warehouse_retrieval(client, api_credentials):
    """Test that warehouse can be retrieved."""
    warehouse = client.get_warehouse(api_credentials["warehouse_id"])
    assert warehouse is not None


def test_assistant_creation(warehouse):
    """Test that knowledge assistant can be created with tools."""
    tools = [SemanticSearchOnChunksTool()]
    assistant = warehouse.get_knowledge_assistant(
        llm_model_id="gpt-4o-mini",
        additional_instructions="Answer in a concise way, in French.",
        tools=tools,
    )
    assert assistant is not None


def test_backend_engineer_skills_query(assistant):
    """Test querying about backend engineer skills."""
    response = assistant.chat("What are the main skills of a backend engineer?")

    # Assert that we got a response
    assert response is not None
    assert len(response) > 0

    # Print response and token usage for debugging
    print(f"Response: {response}")
    print(f"Used tokens: {assistant.get_used_tokens()}")
    print("-*-" * 20)

    response = assistant.chat("merci beaucoup, c'est parfait. Je n'ai plus besoin de rien.")

    # Assert that we got a response
    assert response is not None
    assert len(response) > 0

    # Print response and token usage for debugging
    print(f"Response: {response}")
    print(f"Used tokens: {assistant.get_used_tokens()}")
    print("-*-" * 20)
