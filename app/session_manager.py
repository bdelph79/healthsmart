# Enhanced Session Management for ADK - Infrastructure Utility
# Copyright 2025 Google LLC - Licensed under Apache License, Version 2.0

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional

from google.adk.sessions import InMemorySessionService


class EnhancedSessionManager:
    """
    Enhanced session management for ADK with automatic cleanup,
    monitoring, and session persistence hooks.

    Wraps ADK's InMemorySessionService to add:
    - Automatic session timeout and cleanup
    - Session metadata tracking
    - Background cleanup task
    - Session statistics for monitoring

    This is infrastructure code that should live at the web app layer,
    not in the agent definition layer.
    """

    def __init__(
        self,
        session_service: InMemorySessionService,
        session_timeout_minutes: int = 30,
        cleanup_interval_minutes: int = 5
    ):
        self.session_service = session_service
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.cleanup_interval = timedelta(minutes=cleanup_interval_minutes)

        # Session tracking
        self.active_sessions: Dict[str, any] = {}  # ADK session objects
        self.session_metadata: Dict[str, dict] = {}  # Session metadata

        # Monitoring
        self.session_stats = {
            'total_created': 0,
            'total_expired': 0,
            'total_ended': 0,
            'active_count': 0
        }

        # Background cleanup task
        self._cleanup_task = None

    async def start(self):
        """Start background session cleanup task"""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        print("✅ Session manager started with automatic cleanup")

    async def stop(self):
        """Stop background cleanup task"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        print("✅ Session manager stopped")

    async def get_or_create_session(
        self,
        user_id: str,
        session_id: Optional[str] = None
    ) -> tuple:
        """
        Get existing session or create new one with full metadata tracking.

        Returns: (adk_session, session_id, is_new)
        """
        # Check for existing session
        if session_id and session_id in self.active_sessions:
            # Validate session not expired
            metadata = self.session_metadata[session_id]
            if datetime.now() - metadata['last_activity'] < self.session_timeout:
                # Update activity time
                metadata['last_activity'] = datetime.now()
                metadata['message_count'] += 1

                return (
                    self.active_sessions[session_id],
                    session_id,
                    False  # Not new
                )
            else:
                # Session expired, clean up and create new
                print(f"⏰ Session {session_id} expired, creating new session")
                await self._cleanup_session(session_id)

        # Create new session
        session = await self.session_service.create_session(
            app_name="healthcare_assistant",
            user_id=user_id
        )
        session_id = session.id

        # Initialize tracking
        self.active_sessions[session_id] = session

        self.session_metadata[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'message_count': 1,
            'ip_address': None,  # Can be set by web app
            'user_agent': None   # Can be set by web app
        }

        # Update stats
        self.session_stats['total_created'] += 1
        self.session_stats['active_count'] = len(self.active_sessions)

        print(f"🆕 New session created: {session_id}")

        return (session, session_id, True)  # Is new

    async def end_session(self, session_id: str, reason: str = "user_ended"):
        """Explicitly end a session"""
        if session_id in self.active_sessions:
            print(f"👋 Ending session {session_id}: {reason}")
            await self._cleanup_session(session_id, reason)

    async def _cleanup_session(self, session_id: str, reason: str = "expired"):
        """Clean up a single session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

        if session_id in self.session_metadata:
            # Optionally: Save to database before deleting
            # await self._persist_session_metadata(self.session_metadata[session_id])
            del self.session_metadata[session_id]

        # Update stats
        if reason == "expired":
            self.session_stats['total_expired'] += 1
        else:
            self.session_stats['total_ended'] += 1

        self.session_stats['active_count'] = len(self.active_sessions)

    async def _cleanup_loop(self):
        """Background task to clean up expired sessions"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval.total_seconds())
                await self._cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Error in cleanup loop: {e}")

    async def _cleanup_expired_sessions(self):
        """Clean up all expired sessions"""
        now = datetime.now()
        expired_sessions = []

        for session_id, metadata in self.session_metadata.items():
            if now - metadata['last_activity'] > self.session_timeout:
                expired_sessions.append(session_id)

        if expired_sessions:
            print(f"🧹 Cleaning up {len(expired_sessions)} expired sessions")
            for session_id in expired_sessions:
                await self._cleanup_session(session_id, "expired")

    def get_session_stats(self) -> dict:
        """Get session statistics for monitoring"""
        return {
            **self.session_stats,
            'active_sessions': list(self.active_sessions.keys()),
            'average_session_duration_minutes': self._calculate_avg_duration()
        }

    def _calculate_avg_duration(self) -> float:
        """Calculate average session duration in minutes"""
        if not self.session_metadata:
            return 0.0

        total_duration = sum(
            (metadata['last_activity'] - metadata['created_at']).total_seconds()
            for metadata in self.session_metadata.values()
        )

        return total_duration / len(self.session_metadata) / 60  # Convert to minutes

    def update_session_metadata(self, session_id: str, metadata: dict):
        """Update session metadata (e.g., from web app)"""
        if session_id in self.session_metadata:
            self.session_metadata[session_id].update(metadata)


__all__ = ["EnhancedSessionManager"]
