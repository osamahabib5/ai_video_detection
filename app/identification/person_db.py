"""
Person Database — SQLite
=========================
Stores enrolled persons and their face embeddings.
Schema:
  persons (id, name, role, enrolled_at)
  embeddings (id, person_id FK, vector BLOB, quality_score, captured_at)
"""
import sqlite3
import struct
import os
from pathlib import Path
from datetime import datetime


class PersonDB:
    """Manages person enrollment and face embedding storage."""

    EMBEDDING_DIM = 128  # expected embedding size

    def __init__(self, db_path='data/faces.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS persons (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    name       TEXT    NOT NULL UNIQUE,
                    role       TEXT    DEFAULT '',
                    enrolled_at TEXT   NOT NULL
                );
                CREATE TABLE IF NOT EXISTS embeddings (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_id     INTEGER NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
                    vector        BLOB   NOT NULL,
                    quality_score REAL   DEFAULT 0.0,
                    captured_at   TEXT   NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_emb_person ON embeddings(person_id);
            """)

    # ================================================================
    #  Enrollment
    # ================================================================

    def enroll(self, name, embeddings, role=''):
        """
        Enroll a new person with one or more face embeddings.

        Args:
            name: person's display name (must be unique)
            embeddings: list of numpy arrays [128,] or list of lists
            role: optional role label (e.g., 'warehouse worker')

        Returns:
            person_id (int), or None if name already exists.
        """
        if self.person_exists(name):
            return None

        now = datetime.now().isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO persons (name, role, enrolled_at) VALUES (?, ?, ?)",
                (name, role, now)
            )
            person_id = cur.lastrowid

            for emb in embeddings:
                # Normalize
                import numpy as np
                vec = np.asarray(emb, dtype=np.float32).flatten()
                if vec.shape[0] != self.EMBEDDING_DIM:
                    raise ValueError(
                        f"Embedding dim mismatch: got {vec.shape[0]}, expected {self.EMBEDDING_DIM}"
                    )
                # L2 normalize
                norm = np.linalg.norm(vec)
                if norm > 0:
                    vec = vec / norm
                quality = float(norm)  # higher norm = more confident face

                blob = vec.tobytes()
                conn.execute(
                    "INSERT INTO embeddings (person_id, vector, quality_score, captured_at) "
                    "VALUES (?, ?, ?, ?)",
                    (person_id, blob, quality, now)
                )

        return person_id

    def person_exists(self, name):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM persons WHERE name = ?", (name,)
            ).fetchone()
            return row is not None

    def count_enrolled(self):
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) FROM persons").fetchone()
            return row[0] if row else 0

    # ================================================================
    #  Identification
    # ================================================================

    def get_all_embeddings(self):
        """
        Return all stored embeddings with person info.

        Returns:
            list of (person_id, person_name, numpy_vector [128,])
        """
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT e.person_id, p.name, e.vector, e.quality_score
                FROM embeddings e
                JOIN persons p ON p.id = e.person_id
                ORDER BY e.quality_score DESC
            """).fetchall()

        import numpy as np
        results = []
        for pid, name, blob, quality in rows:
            vec = np.frombuffer(blob, dtype=np.float32)
            if vec.shape[0] == self.EMBEDDING_DIM:
                results.append((pid, name, vec, quality))
        return results

    def identify(self, query_embedding, threshold=0.6):
        """
        Find the closest matching person for a query embedding.

        Args:
            query_embedding: numpy array [128,]
            threshold: cosine similarity threshold (0.0-1.0)

        Returns:
            (person_id, person_name, confidence) or (None, 'UNKNOWN_PERSON', 0.0)
        """
        import numpy as np
        query = np.asarray(query_embedding, dtype=np.float32).flatten()
        q_norm = np.linalg.norm(query)
        if q_norm < 1e-8:
            return None, 'NO_FACE_DETECTED', 0.0

        query = query / q_norm

        best_sim = -1.0
        best_pid = None
        best_name = None

        for pid, name, vec, quality in self.get_all_embeddings():
            sim = float(np.dot(query, vec))  # cosine similarity (both unit vectors)
            if sim > best_sim:
                best_sim = sim
                best_pid = pid
                best_name = name

        if best_sim >= threshold:
            return best_pid, best_name, float(best_sim)
        return None, 'UNKNOWN_PERSON', float(best_sim)

    # ================================================================
    #  Management
    # ================================================================

    def list_persons(self):
        """Return all enrolled persons."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, name, role, enrolled_at FROM persons ORDER BY name"
            ).fetchall()
        return [dict(zip(['id', 'name', 'role', 'enrolled_at'], r)) for r in rows]

    def delete_person(self, person_id):
        with self._connect() as conn:
            conn.execute("DELETE FROM persons WHERE id = ?", (person_id,))

    def delete_all(self):
        with self._connect() as conn:
            conn.execute("DELETE FROM embeddings")
            conn.execute("DELETE FROM persons")
