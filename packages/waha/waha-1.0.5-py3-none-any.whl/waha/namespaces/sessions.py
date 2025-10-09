"""
Sessions namespace for WAHA

Handles session management operations (create, start, stop, restart, etc.).
"""

from typing import List, Optional, Dict, Any
from ..http_client import SyncHTTPClient, AsyncHTTPClient
from ..types import (
    SessionCreateRequest,
    SessionUpdateRequest,
    SessionDTO,
    SessionInfo,
    MeInfo,
)


class SessionsNamespace:
    """Synchronous session operations."""

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def list(self, all: Optional[bool] = None) -> List[SessionInfo]:
        """
        List all sessions.

        Args:
            all: Return all sessions, including those in STOPPED state

        Returns:
            List of session information

        Example:
            sessions = client.sessions.list()
            active_sessions = client.sessions.list(all=False)
        """
        params = {}
        if all is not None:
            params["all"] = all

        response = self._http_client.get("/api/sessions", params=params)
        return [SessionInfo(**session) for session in response]

    def create(
        self,
        name: str,
        config: Optional[Dict[str, Any]] = None,
        start: bool = True,
    ) -> SessionDTO:
        """
        Create a new session.

        Args:
            name: Session name
            config: Session configuration
            start: Whether to start the session immediately

        Returns:
            Created session information

        Example:
            session = client.sessions.create("my-session", start=True)
        """
        request_data = SessionCreateRequest(
            name=name,
            config=config,
            start=start,
        )
        response = self._http_client.post("/api/sessions", data=request_data)
        return SessionDTO(**response)

    def get(self, session: str = "default") -> SessionInfo:
        """
        Get session information.

        Args:
            session: Session name

        Returns:
            Session information

        Example:
            session_info = client.sessions.get("default")
        """
        response = self._http_client.get(f"/api/sessions/{session}")
        return SessionInfo(**response)

    def update(
        self,
        session: str = "default",
        config: Optional[Dict[str, Any]] = None,
        stop: bool = False,
        start: bool = False,
    ) -> SessionDTO:
        """
        Update a session.

        Args:
            session: Session name
            config: Updated session configuration
            stop: Whether to stop the session
            start: Whether to start the session

        Returns:
            Updated session information

        Example:
            session = client.sessions.update("default", config={"debug": True})
        """
        request_data = SessionUpdateRequest(
            config=config,
            stop=stop,
            start=start,
        )
        response = self._http_client.put(f"/api/sessions/{session}", data=request_data)
        return SessionDTO(**response)

    def delete(self, session: str = "default") -> Dict[str, Any]:
        """
        Delete the session.

        Stop and logout the session, then delete it. This is an idempotent operation.

        Args:
            session: Session name

        Returns:
            Response from the API

        Example:
            client.sessions.delete("my-session")
        """
        return self._http_client.delete(f"/api/sessions/{session}")

    def get_me(self, session: str = "default") -> MeInfo:
        """
        Get information about the authenticated account.

        Args:
            session: Session name

        Returns:
            Account information

        Example:
            me = client.sessions.get_me("default")
            print(f"My WhatsApp ID: {me.id}")
        """
        response = self._http_client.get(f"/api/sessions/{session}/me")
        return MeInfo(**response)

    def start(self, session: str = "default") -> SessionDTO:
        """
        Start the session.

        The session must exist. This is an idempotent operation.

        Args:
            session: Session name

        Returns:
            Session information

        Example:
            session = client.sessions.start("default")
        """
        response = self._http_client.post(f"/api/sessions/{session}/start")
        return SessionDTO(**response)

    def stop(self, session: str = "default") -> SessionDTO:
        """
        Stop the session.

        This is an idempotent operation.

        Args:
            session: Session name

        Returns:
            Session information

        Example:
            session = client.sessions.stop("default")
        """
        response = self._http_client.post(f"/api/sessions/{session}/stop")
        return SessionDTO(**response)

    def logout(self, session: str = "default") -> SessionDTO:
        """
        Logout from the session.

        Logout the session, restart a session if it was not STOPPED.

        Args:
            session: Session name

        Returns:
            Session information

        Example:
            session = client.sessions.logout("default")
        """
        response = self._http_client.post(f"/api/sessions/{session}/logout")
        return SessionDTO(**response)

    def restart(self, session: str = "default") -> SessionDTO:
        """
        Restart the session.

        Args:
            session: Session name

        Returns:
            Session information

        Example:
            session = client.sessions.restart("default")
        """
        response = self._http_client.post(f"/api/sessions/{session}/restart")
        return SessionDTO(**response)


class AsyncSessionsNamespace:
    """Asynchronous session operations."""

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def list(self, all: Optional[bool] = None) -> List[SessionInfo]:
        """
        List all sessions.

        Args:
            all: Return all sessions, including those in STOPPED state

        Returns:
            List of session information

        Example:
            sessions = await client.sessions.list()
            active_sessions = await client.sessions.list(all=False)
        """
        params = {}
        if all is not None:
            params["all"] = all

        response = await self._http_client.get("/api/sessions", params=params)
        return [SessionInfo(**session) for session in response]

    async def create(
        self,
        name: str,
        config: Optional[Dict[str, Any]] = None,
        start: bool = True,
    ) -> SessionDTO:
        """
        Create a new session.

        Args:
            name: Session name
            config: Session configuration
            start: Whether to start the session immediately

        Returns:
            Created session information

        Example:
            session = await client.sessions.create("my-session", start=True)
        """
        request_data = SessionCreateRequest(
            name=name,
            config=config,
            start=start,
        )
        response = await self._http_client.post("/api/sessions", data=request_data)
        return SessionDTO(**response)

    async def get(self, session: str = "default") -> SessionInfo:
        """
        Get session information.

        Args:
            session: Session name

        Returns:
            Session information

        Example:
            session_info = await client.sessions.get("default")
        """
        response = await self._http_client.get(f"/api/sessions/{session}")
        return SessionInfo(**response)

    async def update(
        self,
        session: str = "default",
        config: Optional[Dict[str, Any]] = None,
        stop: bool = False,
        start: bool = False,
    ) -> SessionDTO:
        """
        Update a session.

        Args:
            session: Session name
            config: Updated session configuration
            stop: Whether to stop the session
            start: Whether to start the session

        Returns:
            Updated session information

        Example:
            session = await client.sessions.update("default", config={"debug": True})
        """
        request_data = SessionUpdateRequest(
            config=config,
            stop=stop,
            start=start,
        )
        response = await self._http_client.put(
            f"/api/sessions/{session}", data=request_data
        )
        return SessionDTO(**response)

    async def delete(self, session: str = "default") -> Dict[str, Any]:
        """
        Delete the session.

        Stop and logout the session, then delete it. This is an idempotent operation.

        Args:
            session: Session name

        Returns:
            Response from the API

        Example:
            await client.sessions.delete("my-session")
        """
        return await self._http_client.delete(f"/api/sessions/{session}")

    async def get_me(self, session: str = "default") -> MeInfo:
        """
        Get information about the authenticated account.

        Args:
            session: Session name

        Returns:
            Account information

        Example:
            me = await client.sessions.get_me("default")
            print(f"My WhatsApp ID: {me.id}")
        """
        response = await self._http_client.get(f"/api/sessions/{session}/me")
        return MeInfo(**response)

    async def start(self, session: str = "default") -> SessionDTO:
        """
        Start the session.

        The session must exist. This is an idempotent operation.

        Args:
            session: Session name

        Returns:
            Session information

        Example:
            session = await client.sessions.start("default")
        """
        response = await self._http_client.post(f"/api/sessions/{session}/start")
        return SessionDTO(**response)

    async def stop(self, session: str = "default") -> SessionDTO:
        """
        Stop the session.

        This is an idempotent operation.

        Args:
            session: Session name

        Returns:
            Session information

        Example:
            session = await client.sessions.stop("default")
        """
        response = await self._http_client.post(f"/api/sessions/{session}/stop")
        return SessionDTO(**response)

    async def logout(self, session: str = "default") -> SessionDTO:
        """
        Logout from the session.

        Logout the session, restart a session if it was not STOPPED.

        Args:
            session: Session name

        Returns:
            Session information

        Example:
            session = await client.sessions.logout("default")
        """
        response = await self._http_client.post(f"/api/sessions/{session}/logout")
        return SessionDTO(**response)

    async def restart(self, session: str = "default") -> SessionDTO:
        """
        Restart the session.

        Args:
            session: Session name

        Returns:
            Session information

        Example:
            session = await client.sessions.restart("default")
        """
        response = await self._http_client.post(f"/api/sessions/{session}/restart")
        return SessionDTO(**response)
