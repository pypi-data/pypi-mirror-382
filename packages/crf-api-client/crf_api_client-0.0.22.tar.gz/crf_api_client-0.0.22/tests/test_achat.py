# ruff: noqa: E501, G004, T201, S101, PLR2004
import asyncio

import pytest
import pytest_asyncio

from crf_api_client.tools import SemanticSearchOnChunksTool


@pytest_asyncio.fixture
async def async_assistant_1(warehouse):
    """Async fixture for creating the first knowledge assistant with tools."""
    return warehouse.get_knowledge_assistant(
        settings={
            "model": "gpt-4o-mini",
            "additional_instructions": "Answer in a concise way, in French.",
            "tools": [SemanticSearchOnChunksTool()],
        }
    )


@pytest_asyncio.fixture
async def async_assistant_2(warehouse):
    """Async fixture for creating the second knowledge assistant with tools."""
    return warehouse.get_knowledge_assistant(
        settings={
            "model": "gpt-4o-mini",
            "additional_instructions": "Answer in a concise way, in French.",
            "tools": [SemanticSearchOnChunksTool()],
        }
    )


@pytest.mark.asyncio
async def test_parallel_assistants(async_assistant_1, async_assistant_2):
    """Test running two assistants in parallel with different queries."""

    async def query_assistant_1():
        """Query for backend engineer skills."""
        response = await async_assistant_1.achat("What are the main skills of a backend engineer?")
        print(f"[Assistant 1] Response: {response}")
        print(f"[Assistant 1] Tokens used: {async_assistant_1.get_used_tokens()}")
        return response

    async def query_assistant_2():
        """Query for frontend engineer skills."""
        response = await async_assistant_2.achat("What are the main skills of a frontend engineer?")
        print(f"[Assistant 2] Response: {response}")
        print(f"[Assistant 2] Tokens used: {async_assistant_2.get_used_tokens()}")
        return response

    # Run both assistants in parallel
    print("Starting parallel assistant queries...")
    print("=" * 50)

    results = await asyncio.gather(query_assistant_1(), query_assistant_2(), return_exceptions=True)

    print("\n" + "=" * 50)
    print("Parallel queries completed!")

    # Check results
    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print(f"Assistant {i} failed with error: {result}")
            pytest.fail(f"Assistant {i} failed: {result}")
        else:
            # Assert that we got a response
            assert result is not None
            assert len(result) > 0

    print("-*-" * 20)


@pytest.mark.asyncio
async def test_parallel_conversations(async_assistant_1, async_assistant_2):
    """Test running two assistants in parallel with multi-turn conversations."""

    async def conversation_1():
        """First conversation: Backend engineering discussion."""
        print("=*= Starting Conversation 1 (Backend) =*=")

        # First message
        response1 = await async_assistant_1.achat("What are the main skills of a backend engineer?")
        print(f"[Conversation 1] Response 1: {response1}")
        print(f"[Conversation 1] Tokens used: {async_assistant_1.get_used_tokens()}")

        # Second message
        response2 = await async_assistant_1.achat(
            "Can you elaborate on database management skills?"
        )
        print(f"[Conversation 1] Response 2: {response2}")
        print(f"[Conversation 1] Tokens used: {async_assistant_1.get_used_tokens()}")

        print("=*= Conversation 1 Complete =*=")
        return [response1, response2]

    async def conversation_2():
        """Second conversation: Frontend engineering discussion."""
        print("=|= Starting Conversation 2 (Frontend) =|=")

        # First message
        response1 = await async_assistant_2.achat(
            "What are the main skills of a frontend engineer?"
        )
        print(f"[Conversation 2] Response 1: {response1}")
        print(f"[Conversation 2] Tokens used: {async_assistant_2.get_used_tokens()}")

        # Second message
        response2 = await async_assistant_2.achat("Can you elaborate on JavaScript frameworks?")
        print(f"[Conversation 2] Response 2: {response2}")
        print(f"[Conversation 2] Tokens used: {async_assistant_2.get_used_tokens()}")

        print("=|= Conversation 2 Complete =|=")
        return [response1, response2]

    # Run both conversations in parallel
    print("Starting parallel conversations...")
    print("=" * 50)

    results = await asyncio.gather(conversation_1(), conversation_2(), return_exceptions=True)

    print("\n" + "=" * 50)
    print("All parallel conversations completed!")

    # Check results
    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print(f"Conversation {i} failed with error: {result}")
            pytest.fail(f"Conversation {i} failed: {result}")
        else:
            # Assert that we got responses
            assert len(result) == 2
            assert all(response is not None and len(response) > 0 for response in result)

    print("-*-" * 20)
