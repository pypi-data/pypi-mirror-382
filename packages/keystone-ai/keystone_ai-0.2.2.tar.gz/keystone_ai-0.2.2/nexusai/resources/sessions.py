"""Session management resource module."""

from typing import Optional, Dict, Any, List, Iterator
from nexusai.models import SessionModel, Message, SessionResponse, Usage


class Session:
    """
    Session object for context-aware multi-turn conversations.

    A session maintains conversation history and agent configuration,
    enabling stateful interactions with AI models.
    """

    def __init__(self, session_data: Dict[str, Any], client):
        """
        Initialize session object.

        Args:
            session_data: Session data from API response
            client: InternalClient instance
        """
        self.id = session_data["session_id"]
        self._data = session_data
        self._client = client

    @property
    def agent_type(self) -> str:
        """Get the agent type."""
        return self._data.get("agent_type", "assistant")

    @property
    def is_active(self) -> bool:
        """Check if session is active."""
        return self._data.get("is_active", True)

    @property
    def agent_config(self) -> Optional[Dict[str, Any]]:
        """Get the agent configuration."""
        return self._data.get("agent_config")

    @property
    def name(self) -> Optional[str]:
        """Get the session name."""
        return self._data.get("name")

    def invoke(self, prompt: str, config: Optional[Dict[str, Any]] = None, **kwargs) -> SessionResponse:
        """
        Send a message in this session (synchronous).

        The session automatically maintains conversation history,
        so you don't need to manually manage context.

        Args:
            prompt: User message content
            config: Optional configuration to temporarily override session settings
                   (e.g., {"temperature": 0.9, "max_tokens": 500})
            **kwargs: Additional parameters (for future compatibility)

        Returns:
            SessionResponse containing assistant's reply

        Raises:
            InvalidRequestError: If request parameters are invalid
            NotFoundError: If session doesn't exist
            APIError: If invocation fails

        Example:
            ```python
            session = client.sessions.create()

            # First message
            response = session.invoke("My name is Alice")
            print(response.response.content)

            # Follow-up message - session remembers context
            response = session.invoke("What's my name?")
            print(response.response.content)  # Will remember "Alice"

            # Temporarily override temperature
            response = session.invoke(
                "Tell me a creative story",
                config={"temperature": 1.2}
            )
            ```
        """
        # Backend expects: {"input": {"prompt": "..."}, "config": {...}, "stream": false}
        request_body = {
            "input": {"prompt": prompt},
            "stream": False,
        }

        # Add config if provided
        if config:
            request_body["config"] = config

        response = self._client.request(
            "POST",
            f"/sessions/{self.id}/invoke",
            json_data=request_body,
        )

        # Parse response - backend returns {"output": {"text": "..."}, "metadata": {...}}
        output_data = response.get("output", {})
        metadata = response.get("metadata", {})
        usage_data = metadata.get("usage")

        # Convert output.text to Message format
        message_data = {
            "role": "assistant",
            "content": output_data.get("text", "")
        }

        return SessionResponse(
            session_id=response.get("session_id", self.id),
            response=Message(**message_data),
            usage=Usage(**usage_data) if usage_data else None,
        )

    def stream(self, prompt: str, **kwargs) -> Iterator[Dict[str, Any]]:
        """
        Send a message in this session with streaming response.

        Args:
            prompt: User message content
            **kwargs: Additional configuration

        Yields:
            Dictionary chunks from streaming response

        Raises:
            InvalidRequestError: If request parameters are invalid
            NotFoundError: If session doesn't exist
            APIError: If streaming fails

        Example:
            ```python
            session = client.sessions.create()

            for chunk in session.stream("Tell me a story"):
                if "delta" in chunk:
                    print(chunk["delta"].get("content", ""), end="", flush=True)
            print()
            ```
        """
        request_body = {
            "prompt": prompt,
            "stream": True,
            **kwargs,
        }

        for chunk in self._client.stream(
            "POST",
            f"/sessions/{self.id}/invoke",
            json_data=request_body,
        ):
            yield chunk

    def history(self, limit: int = 20, offset: int = 0) -> List[Message]:
        """
        Get conversation history for this session.

        Args:
            limit: Maximum number of messages to return. Default: 20
            offset: Number of messages to skip. Default: 0

        Returns:
            List of Message objects in chronological order

        Raises:
            NotFoundError: If session doesn't exist
            APIError: If retrieval fails

        Example:
            ```python
            session = client.sessions.get("sess_abc123")

            # Get last 10 messages
            messages = session.history(limit=10)
            for msg in messages:
                print(f"{msg.role}: {msg.content}")
            ```
        """
        response = self._client.request(
            "GET",
            f"/sessions/{self.id}/history",
            params={"limit": limit, "offset": offset},
        )

        messages = response.get("messages", [])
        return [Message(**msg) for msg in messages]

    def delete(self) -> None:
        """
        Delete this session and all its history.

        This is a permanent action that cannot be undone.

        Raises:
            NotFoundError: If session doesn't exist
            APIError: If deletion fails

        Example:
            ```python
            session = client.sessions.create()
            # ... use session ...
            session.delete()  # Clean up when done
            ```
        """
        self._client.request("DELETE", f"/sessions/{self.id}")
        self._data["is_active"] = False

    def __repr__(self) -> str:
        """Return string representation of session."""
        return f"Session(id='{self.id}', agent_type='{self.agent_type}', active={self.is_active})"


class SessionsResource:
    """
    Session management resource.

    Provides methods for creating, retrieving, and managing conversation sessions.
    """

    def __init__(self, client):
        """
        Initialize sessions resource.

        Args:
            client: InternalClient instance
        """
        self._client = client

    def create(
        self,
        agent_type: str = "assistant",
        agent_config: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        **kwargs,
    ) -> Session:
        """
        Create a new conversation session.

        Args:
            agent_type: Type of agent. Default: "assistant"
            agent_config: Agent configuration including model, temperature, etc.
            name: Optional name for the session
            **kwargs: Additional session parameters

        Returns:
            Session object ready for conversation

        Raises:
            InvalidRequestError: If parameters are invalid
            APIError: If creation fails

        Example:
            ```python
            from nexusai import NexusAIClient

            client = NexusAIClient()

            # Simple mode
            session = client.sessions.create()

            # With configuration
            session = client.sessions.create(
                agent_type="assistant",
                agent_config={
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "system_prompt": "You are a helpful coding assistant"
                },
                name="Code Help Session"
            )

            response = session.invoke("Hello!")
            print(response.response.content)
            ```
        """
        request_body = {
            "agent_type": agent_type,
            **kwargs,
        }

        if agent_config:
            request_body["agent_config"] = agent_config
        if name:
            request_body["name"] = name

        response = self._client.request("POST", "/sessions", json_data=request_body)
        return Session(response, self._client)

    def get(self, session_id: str) -> Session:
        """
        Retrieve an existing session.

        Args:
            session_id: Unique session identifier

        Returns:
            Session object

        Raises:
            NotFoundError: If session doesn't exist
            APIError: If retrieval fails

        Example:
            ```python
            # Get a previously created session
            session = client.sessions.get("sess_abc123def456")
            response = session.invoke("Continue our conversation")
            ```
        """
        response = self._client.request("GET", f"/sessions/{session_id}")
        return Session(response, self._client)

    def list(self, page: int = 1, per_page: int = 20) -> List[SessionModel]:
        """
        List all sessions for the current API key.

        Args:
            page: Page number (1-indexed). Default: 1
            per_page: Number of sessions per page. Default: 20

        Returns:
            List of SessionModel objects

        Raises:
            APIError: If retrieval fails

        Example:
            ```python
            # List all sessions
            sessions = client.sessions.list()
            for session in sessions:
                print(f"{session.name}: {session.session_id}")

            # Paginated retrieval
            page1 = client.sessions.list(page=1, per_page=10)
            page2 = client.sessions.list(page=2, per_page=10)
            ```
        """
        response = self._client.request(
            "GET",
            "/sessions",
            params={"page": page, "per_page": per_page},
        )

        sessions = response.get("sessions", [])
        return [SessionModel(**s) for s in sessions]
