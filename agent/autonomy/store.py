"""Durable SQLite run store used for checkpointing and process recovery."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from agent.autonomy.models import AgentRun


class RunNotFoundError(KeyError):
    pass


class SQLiteRunStore:
    def __init__(self, path: str | Path = "data/helixagent_runs.db") -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path, check_same_thread=False)
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS agent_runs "
            "(id TEXT PRIMARY KEY, state_json TEXT NOT NULL, updated_at TEXT NOT NULL)"
        )
        self._connection.commit()

    def save(self, run: AgentRun) -> None:
        run.touch()
        self._connection.execute(
            "INSERT INTO agent_runs(id, state_json, updated_at) VALUES (?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET state_json=excluded.state_json, "
            "updated_at=excluded.updated_at",
            (run.id, run.model_dump_json(), run.updated_at.isoformat()),
        )
        self._connection.commit()

    def get(self, run_id: str) -> AgentRun:
        row = self._connection.execute(
            "SELECT state_json FROM agent_runs WHERE id = ?", (run_id,)
        ).fetchone()
        if row is None:
            raise RunNotFoundError(run_id)
        return AgentRun.model_validate_json(row[0])
