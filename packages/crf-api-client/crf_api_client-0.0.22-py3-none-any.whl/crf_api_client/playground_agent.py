# ruff: noqa: DTZ005, C901, PLR0912, E501, ANN003, D205, D105
import json
import logging
from datetime import datetime
from typing import Optional

import requests

from .base import BaseAPIClient

logger = logging.getLogger(__name__)


class PlaygroundAgent(BaseAPIClient):
    def __init__(
        self,
        base_url: str,
        token: str,
        warehouse_id: str,
        agent_settings_id: str,
        **kwargs,
    ):
        super().__init__(base_url, token)
        self.warehouse_id = warehouse_id
        self.agent_settings_id = agent_settings_id
        # Store any additional agent attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def create_conversation(self) -> dict:
        """Create a new playground conversation"""
        url = f"{self.base_url}/api/v1/projects/{self.warehouse_id}/playground-conversations/"
        data = {
            "name": f"Playground {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            "type": "playground",
            "agent_settings": self.agent_settings_id,
        }
        response = requests.post(url, headers=self._get_headers(), json=data)
        response.raise_for_status()
        return response.json()

    def send_message(
        self, conversation_id: str, message_text: str, version_hash: Optional[str] = None
    ) -> str:
        """Send a message to a conversation and return the assistant's response"""
        if version_hash is None:
            # Get the conversation to retrieve version_hash
            conversation = self._get_conversation(conversation_id)
            version_hash = conversation.get("version_hash")
            if not version_hash:
                raise ValueError("Could not retrieve version_hash for conversation")

        url = f"{self.base_url}/api/v1/projects/{self.warehouse_id}/playground-conversations/{conversation_id}/send_message_stream/"
        data = {"message": message_text, "version_hash": version_hash}

        # Enable streaming for the request
        response = requests.post(url, headers=self._get_headers(), json=data, stream=True)
        response.raise_for_status()

        # Process streaming response - only keep the last message
        last_message = None
        for line in response.iter_lines(decode_unicode=True):
            if line:
                # Handle Server-Sent Events format
                if line.startswith("data: "):
                    try:
                        # Extract JSON data from SSE format
                        json_data = line[6:]  # Remove 'data: ' prefix
                        if json_data.strip() == "[DONE]":
                            break
                        event_data = json.loads(json_data)

                        # Look for the streaming_completed event which contains the final response
                        if event_data.get("type_streaming") == "streaming_completed":
                            # Extract the assistant's message from chat_history
                            chat_history = event_data.get("payload", {}).get("chat_history", [])
                            for msg in reversed(chat_history):  # Start from the end
                                if msg.get("role") == "assistant" and msg.get("type") == "message":
                                    last_message = msg.get("content", "")
                                    break
                        elif event_data.get("type_streaming") == "streaming_in_progress":
                            # Keep track of the latest message during streaming
                            payload = event_data.get("payload", {})
                            if (
                                payload.get("type") == "message"
                                and payload.get("role") == "assistant"
                            ):
                                last_message = payload.get("content", "")

                    except json.JSONDecodeError:
                        continue
                elif line.startswith("event: "):
                    # Handle event type if needed
                    continue
                elif line.strip() == "":
                    # Empty line separator in SSE
                    continue
                else:
                    # Try to parse as regular JSON (fallback)
                    try:
                        event_data = json.loads(line)

                        # Apply same logic for non-SSE format
                        if event_data.get("type_streaming") == "streaming_completed":
                            chat_history = event_data.get("payload", {}).get("chat_history", [])
                            for msg in reversed(chat_history):
                                if msg.get("role") == "assistant" and msg.get("type") == "message":
                                    last_message = msg.get("content", "")
                                    break
                    except json.JSONDecodeError:
                        continue

        return last_message or ""

    def create_conversation_and_send_message(self, message_text: str) -> dict:
        """
        Create a new conversation and send a message
        Returns conversation details with the assistant's response
        """
        conversation = self.create_conversation()
        conversation_id = conversation["id"]
        version_hash = conversation.get("version_hash")

        answer = self.send_message(conversation_id, message_text, version_hash)

        return {
            "conversation_id": conversation_id,
            "query": message_text,
            "answer": answer,
            "agent_settings_id": self.agent_settings_id,
            "version_hash": version_hash,
        }

    def _get_conversation(self, conversation_id: str) -> dict:
        """Get conversation details by ID"""
        url = f"{self.base_url}/api/v1/projects/{self.warehouse_id}/playground-conversations/{conversation_id}/"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def list_conversations(self) -> list[dict]:
        """List all playground conversations for this agent"""
        url = f"{self.base_url}/api/v1/projects/{self.warehouse_id}/playground-conversations/"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json().get("results", [])

    def get_conversation_history(self, conversation_id: str) -> list[dict]:
        """Get the full conversation history"""
        conversation = self._get_conversation(conversation_id)
        return conversation.get("chat_history", [])

    def __repr__(self):
        return (
            f"PlaygroundAgent(agent_settings_id='{self.agent_settings_id}', "
            f"warehouse_id='{self.warehouse_id}')"
        )

    def __str__(self):
        return f"PlaygroundAgent: {self.agent_settings_id} (warehouse: {self.warehouse_id})"
