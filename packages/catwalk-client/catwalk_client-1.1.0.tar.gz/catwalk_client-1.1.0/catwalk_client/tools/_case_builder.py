from __future__ import annotations

from typing import Any


class CaseBuilder:
    def __init__(self, client):
        self._client = client
        self._track_id = None
        self._query: list[dict] = []
        self._context: list[dict] = []
        self._response: list[dict] = []
        self._metadata: dict = {}

    def set_track_id(self, track_id: str):
        self._track_id = track_id
        return self

    def add_query(self, name: str, value: Any, type: str | dict):
        self._query.append({"name": name, "value": value, "type": type})
        return self

    def add_context(self, name: str, value: Any, type: str | dict):
        self._context.append({"name": name, "value": value, "type": type})
        return self

    def add_response(
        self,
        name: str,
        value: Any,
        type: str | dict,
    ):
        self._response.append({"name": name, "value": value, "type": type})
        return self

    def set_metadata(self, **kwargs):
        self._metadata = kwargs
        return self

    def send(self):
        self._client.send(
            {
                "track_id": self._track_id,
                "query": self._query,
                "context": self._context,
                "response": self._response,
                "metadata": self._metadata,
            }
        )

    def update(self):
        """Update the case details (`query`, `context`, `response`, `metadata`)."""
        data = {
            "query": self._query,
            "context": self._context,
            "response": self._response,
            "metadata": self._metadata,
        }

        self._client.update(self._track_id, data)
