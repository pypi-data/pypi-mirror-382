"""SQLite backend implementation."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from sifts.io.db.base import DatabaseBackend
from sifts.io.db.types import AnalysisFacet, SafeFacet, SnippetFacet, VulnerableFacet


class SQLiteBackend(DatabaseBackend):
    """SQLite implementation of the database backend."""

    def __init__(self, database_path: str | Path = "sifts.db") -> None:
        """Initialize SQLite backend."""
        self.database_path = Path(database_path)
        self.connection: sqlite3.Connection | None = None

    async def startup(self) -> None:
        """Initialize the SQLite connection and create tables."""
        if self.connection is not None:
            return

        # Ensure the directory exists
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(str(self.database_path))
        self.connection.row_factory = sqlite3.Row  # Enable column access by name

        # Create tables
        await self._create_tables()

    async def shutdown(self) -> None:
        """Close the SQLite connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def _get_connection(self) -> sqlite3.Connection:
        """Get the SQLite connection."""
        if self.connection is None:
            msg = "SQLite backend not initialized. Call startup() first."
            raise RuntimeError(msg)
        return self.connection

    async def _create_tables(self) -> None:
        """Create the necessary tables."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create snippets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snippets (
                snippet_hash_id TEXT NOT NULL,
                group_name TEXT NOT NULL,
                root_nickname TEXT NOT NULL,
                'commit' TEXT NOT NULL,
                path TEXT NOT NULL,
                start_byte INTEGER NOT NULL,
                end_byte INTEGER NOT NULL,
                start_line INTEGER NOT NULL,
                start_column INTEGER NOT NULL,
                end_line INTEGER NOT NULL,
                end_column INTEGER NOT NULL,
                node_type TEXT NOT NULL,
                code_sha256 TEXT NOT NULL,
                created_at TEXT NOT NULL,
                text TEXT,
                language TEXT,
                name TEXT,
                PRIMARY KEY (snippet_hash_id)
            )
        """)

        # Create analysis table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis (
                group_name TEXT NOT NULL,
                root_nickname TEXT NOT NULL,
                version TEXT NOT NULL,
                file_path TEXT NOT NULL,
                snippet_hash_id TEXT NOT NULL,
                code_hash TEXT NOT NULL,
                vulnerability_id_candidates TEXT NOT NULL,  -- JSON array
                analyzed_at TEXT NOT NULL,
                candidate_index INTEGER,
                'commit' TEXT NOT NULL,
                cost REAL NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL,
                total_tokens INTEGER NOT NULL,
                vulnerable BOOLEAN NOT NULL,
                ranking_score REAL,
                reason TEXT NOT NULL,
                vulnerable_lines TEXT,  -- JSON array
                suggested_criteria_code TEXT,
                suggested_finding_title TEXT,
                trace_id TEXT,
                path TEXT NOT NULL,
                PRIMARY KEY (group_name, root_nickname, version,
                file_path, snippet_hash_id, vulnerability_id_candidates)
            )
        """)

        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_snippets_group_root
            ON snippets (group_name, root_nickname)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_snippets_path
            ON snippets (group_name, root_nickname, path)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_analysis_group_root_version
            ON analysis (group_name, root_nickname, version)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_analysis_snippet
            ON analysis (group_name, root_nickname, version, file_path, snippet_hash_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_analysis_vulnerable
            ON analysis (group_name, root_nickname, version, vulnerable)
        """)

        conn.commit()

    @staticmethod
    def _serialize_for_sqlite(value: Any) -> Any:  # noqa: ANN401
        """Convert Python types to SQLite-compatible types."""
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, (list, tuple, set)):
            return json.dumps(list(value))
        if isinstance(value, dict):
            return json.dumps(value)
        return value

    @staticmethod
    def _deserialize_from_sqlite(value: str, field_type: str) -> Any:  # noqa: ANN401
        """Convert SQLite values back to Python types."""
        if field_type in ("vulnerability_id_candidates", "vulnerable_lines") and value:
            return json.loads(value)
        return value

    async def insert_snippet(self, snippet: SnippetFacet) -> None:
        """Insert a snippet into SQLite."""
        conn = self._get_connection()
        cursor = conn.cursor()

        data = snippet.model_dump()
        cursor.execute(
            """
            INSERT OR REPLACE INTO snippets (
                snippet_hash_id, group_name, root_nickname, 'commit', path,
                start_byte, end_byte, start_line, start_column, end_line,
                end_column, node_type, code_sha256, created_at, text,
                language, name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data["snippet_hash_id"],
                data["group_name"],
                data["root_nickname"],
                data["commit"],
                data["path"],
                data["start_byte"],
                data["end_byte"],
                data["start_line"],
                data["start_column"],
                data["end_line"],
                data["end_column"],
                data["node_type"],
                data["code_sha256"],
                data["created_at"].isoformat()
                if isinstance(data["created_at"], datetime)
                else data["created_at"],
                data.get("text"),
                data.get("language"),
                data.get("name"),
            ),
        )

        conn.commit()

    async def insert_analysis(self, analysis: AnalysisFacet) -> None:
        """Insert an analysis result into SQLite."""
        conn = self._get_connection()
        cursor = conn.cursor()

        data = analysis.model_dump()
        vulnerability_candidates = self._serialize_for_sqlite(data["vulnerability_id_candidates"])
        vulnerable_lines = self._serialize_for_sqlite(data.get("vulnerable_lines", []))

        cursor.execute(
            """
            INSERT OR REPLACE INTO analysis (
                group_name, root_nickname, version, file_path, snippet_hash_id,
                code_hash, vulnerability_id_candidates, analyzed_at, candidate_index,
                'commit', cost, input_tokens, output_tokens, total_tokens, vulnerable,
                ranking_score, reason, vulnerable_lines, suggested_criteria_code,
                suggested_finding_title, trace_id, path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data["group_name"],
                data["root_nickname"],
                data["version"],
                data["path"],  # Use path instead of file_path
                data["snippet_hash_id"],
                data["code_hash"],
                vulnerability_candidates,
                data["analyzed_at"].isoformat()
                if isinstance(data["analyzed_at"], datetime)
                else data["analyzed_at"],
                data.get("candidate_index"),
                data["commit"],
                data["cost"],
                data["input_tokens"],
                data["output_tokens"],
                data["total_tokens"],
                data["vulnerable"],
                data.get("ranking_score"),
                data["reason"],
                vulnerable_lines,
                data.get("suggested_criteria_code"),
                data.get("suggested_finding_title"),
                data.get("trace_id"),
                data["path"],
            ),
        )

        conn.commit()

    async def get_snippets_by_root(self, group_name: str, root_nickname: str) -> list[SnippetFacet]:
        """Get all snippets for a specific root."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM snippets
            WHERE group_name = ? AND root_nickname = ?
        """,
            (group_name, root_nickname),
        )

        rows = cursor.fetchall()
        return [self._row_to_snippet(row) for row in rows]

    async def get_snippets_by_file_path(
        self,
        group_name: str,
        root_nickname: str,
        path: str,
    ) -> list[SnippetFacet]:
        """Get all snippets for a specific file path."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM snippets
            WHERE group_name = ? AND root_nickname = ? AND path = ?
        """,
            (group_name, root_nickname, path),
        )

        rows = cursor.fetchall()
        return [self._row_to_snippet(row) for row in rows]

    async def get_analyses_for_snippet(
        self,
        group_name: str,
        root_nickname: str,
        version: str,
        path: str,
        code_sha256: str,
    ) -> list[AnalysisFacet]:
        """Get all analyses for a specific snippet and version."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM analysis
            WHERE group_name = ? AND root_nickname = ? AND version = ?
            AND file_path = ? AND code_hash = ?
        """,
            (group_name, root_nickname, version, path, code_sha256),
        )

        rows = cursor.fetchall()
        return [self._row_to_analysis(row) for row in rows]

    async def get_analyses_by_file_path_version(
        self,
        group_name: str,
        root_nickname: str,
        version: str,
        path: str,
    ) -> list[AnalysisFacet]:
        """Get all analyses for a file path within a given version."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM analysis
            WHERE group_name = ? AND root_nickname = ? AND version = ? AND file_path = ?
        """,
            (group_name, root_nickname, version, path),
        )

        rows = cursor.fetchall()
        return [self._row_to_analysis(row) for row in rows]

    async def get_analyses_for_snippet_vulnerability(  # noqa: PLR0913
        self,
        group_name: str,
        root_nickname: str,
        version: str,
        path: str,
        code_sha256: str,
        vulnerability_id: str,
    ) -> list[AnalysisFacet]:
        """Get analyses for a specific snippet and vulnerability."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM analysis
            WHERE group_name = ? AND root_nickname = ? AND version = ?
            AND file_path = ? AND code_hash = ?
            AND vulnerability_id_candidates LIKE ?
        """,
            (
                group_name,
                root_nickname,
                version,
                path,
                code_sha256,
                f'%"{vulnerability_id}"%',
            ),
        )

        rows = cursor.fetchall()
        return [self._row_to_analysis(row) for row in rows]

    async def get_snippet_by_hash(
        self,
        group_name: str,
        root_nickname: str,
        path: str,
        code_sha256: str,
    ) -> SnippetFacet | None:
        """Get a specific snippet by its hash."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM snippets
            WHERE group_name = ? AND root_nickname = ? AND path = ? AND code_sha256 = ?
        """,
            (group_name, root_nickname, path, code_sha256),
        )

        row = cursor.fetchone()
        if row is None:
            return None

        return self._row_to_snippet(row)

    async def get_analyses_by_root(
        self,
        group_name: str,
        root_nickname: str,
        version: str,
        commit: str | None = None,
    ) -> list[AnalysisFacet]:
        """Get all analyses for a root, optionally filtered by commit."""
        conn = self._get_connection()
        cursor = conn.cursor()

        query = """
            SELECT * FROM analysis
            WHERE group_name = ? AND root_nickname = ? AND version = ? AND vulnerable = 1
        """
        params = [group_name, root_nickname, version]

        if commit:
            query += " AND commit = ?"
            params.append(commit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [self._row_to_analysis(row) for row in rows]

    @staticmethod
    def _row_to_snippet(row: sqlite3.Row) -> SnippetFacet:
        """Convert a SQLite row to a SnippetFacet."""
        # Convert created_at from string to datetime if needed
        created_at = row["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        return SnippetFacet(
            snippet_hash_id=row["snippet_hash_id"],
            group_name=row["group_name"],
            root_nickname=row["root_nickname"],
            commit=row["commit"],
            path=row["path"],
            start_byte=row["start_byte"],
            end_byte=row["end_byte"],
            start_line=row["start_line"],
            start_column=row["start_column"],
            end_line=row["end_line"],
            end_column=row["end_column"],
            node_type=row["node_type"],
            code_sha256=row["code_sha256"],
            created_at=created_at,
            text=row["text"],
            language=row["language"],
            name=row["name"],
        )

    @staticmethod
    def _row_to_analysis(row: sqlite3.Row) -> AnalysisFacet:
        """Convert a SQLite row to an AnalysisFacet."""
        # Parse JSON fields
        vulnerability_candidates = SQLiteBackend._deserialize_from_sqlite(
            row["vulnerability_id_candidates"], "vulnerability_id_candidates"
        )
        vulnerable_lines = SQLiteBackend._deserialize_from_sqlite(
            row["vulnerable_lines"], "vulnerable_lines"
        )

        # Convert analyzed_at to datetime if it's a string
        analyzed_at = row["analyzed_at"]
        if isinstance(analyzed_at, str):
            analyzed_at = datetime.fromisoformat(analyzed_at)

        # Base fields common to both Vulnerable and Safe facets
        base_fields = {
            "group_name": row["group_name"],
            "root_nickname": row["root_nickname"],
            "version": row["version"],
            "commit": row["commit"],
            "analyzed_at": analyzed_at,
            "file_path": row["file_path"],
            "path": row["path"],
            "cost": row["cost"],
            "candidate_index": row["candidate_index"],
            "trace_id": row["trace_id"],
            "vulnerability_id_candidates": vulnerability_candidates,
            "input_tokens": row["input_tokens"],
            "output_tokens": row["output_tokens"],
            "total_tokens": row["total_tokens"],
            "reason": row["reason"],
            "code_hash": row["code_hash"],
            "snippet_hash_id": row["snippet_hash_id"],
        }

        if row["vulnerable"]:
            return VulnerableFacet(
                **base_fields,
                vulnerable=True,
                vulnerable_lines=vulnerable_lines or [],
                ranking_score=row["ranking_score"],
                suggested_criteria_code=row["suggested_criteria_code"],
                suggested_finding_title=row["suggested_finding_title"],
            )
        return SafeFacet(
            **base_fields,
            vulnerable=False,
            vulnerable_lines=vulnerable_lines,
            ranking_score=row["ranking_score"],
            suggested_criteria_code=row["suggested_criteria_code"],
            suggested_finding_title=row["suggested_finding_title"],
        )
