from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import psycopg
from psycopg.types.json import Json


@dataclass(frozen=True)
class DBConfig:
    """note: Holds database connection configuration for Postgres + pgvector."""
    dsn: str


def _column_exists(conn: psycopg.Connection, table: str, column: str) -> bool:
    """note: Returns True if the given column exists on the given table in the public schema."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = %s
                  AND column_name = %s
            );
            """,
            (table, column),
        )
        row = cur.fetchone()
        return bool(row[0]) if row else False


def migrate_corpus_label(conn: psycopg.Connection) -> None:
    """note: Lightweight migration — adds corpus_label column + fixes UNIQUE constraint if missing.

    Safe to call before ensure_schema(); requires no embedding_dim. Idempotent.
    """
    if not _column_exists(conn, "rag_chunks", "corpus_label"):
        with conn.cursor() as cur:
            cur.execute(
                "ALTER TABLE rag_chunks ADD COLUMN corpus_label TEXT NOT NULL DEFAULT '';"
            )
        conn.commit()

    # Fix old two-column UNIQUE constraint if it still exists
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT conname FROM pg_constraint
            WHERE conrelid = 'rag_chunks'::regclass
              AND contype = 'u'
              AND array_length(conkey, 1) = 2;
            """
        )
        old_uq = cur.fetchone()
        if old_uq is not None:
            old_conname = old_uq[0]
            cur.execute(f"ALTER TABLE rag_chunks DROP CONSTRAINT IF EXISTS {old_conname};")
            cur.execute(
                """
                ALTER TABLE rag_chunks
                ADD CONSTRAINT rag_chunks_corpus_doc_chunk_key
                UNIQUE (corpus_label, doc_sha256, chunk_index);
                """
            )
            conn.commit()

    with conn.cursor() as cur:
        cur.execute(
            "CREATE INDEX IF NOT EXISTS rag_chunks_corpus_label_idx ON rag_chunks (corpus_label);"
        )
    conn.commit()


def ensure_schema(conn: psycopg.Connection, embedding_dim: int) -> None:
    """note: Creates required tables and indexes for chunk storage and vector search.

    Safe to call on an existing DB:
    - CREATE TABLE IF NOT EXISTS guards all table creation.
    - ALTER TABLE ... ADD COLUMN IF NOT EXISTS adds corpus_label when migrating.
    - Drops and recreates the UNIQUE constraint to include corpus_label when the
      old (doc_sha256, chunk_index) constraint exists without corpus_label.
    """
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS rag_meta (
                k TEXT PRIMARY KEY,
                v TEXT NOT NULL,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            """
        )

        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS rag_chunks (
                id BIGSERIAL PRIMARY KEY,
                corpus_label TEXT NOT NULL DEFAULT '',
                doc_path TEXT NOT NULL,
                doc_sha256 TEXT NOT NULL,
                chunk_index INT NOT NULL,
                chunk_text TEXT NOT NULL,
                embedding VECTOR({int(embedding_dim)}) NOT NULL,
                meta JSONB NOT NULL DEFAULT '{{}}'::jsonb,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                UNIQUE (corpus_label, doc_sha256, chunk_index)
            );
            """
        )

    # --- Migration: add corpus_label column if it was missing ---
    if not _column_exists(conn, "rag_chunks", "corpus_label"):
        with conn.cursor() as cur:
            cur.execute(
                "ALTER TABLE rag_chunks ADD COLUMN corpus_label TEXT NOT NULL DEFAULT '';"
            )

    # --- Migration: fix the UNIQUE constraint to include corpus_label ---
    # The old constraint was (doc_sha256, chunk_index).  If that still exists
    # without corpus_label we drop it and add the correct three-column one.
    with conn.cursor() as cur:
        # Check whether the old two-column constraint still exists by inspecting
        # the constraint definition through pg_constraint.
        cur.execute(
            """
            SELECT conname
            FROM pg_constraint
            WHERE conrelid = 'rag_chunks'::regclass
              AND contype = 'u'
              AND array_length(conkey, 1) = 2;
            """
        )
        old_uq = cur.fetchone()
        if old_uq is not None:
            old_conname = old_uq[0]
            cur.execute(f"ALTER TABLE rag_chunks DROP CONSTRAINT IF EXISTS {old_conname};")
            cur.execute(
                """
                ALTER TABLE rag_chunks
                ADD CONSTRAINT rag_chunks_corpus_doc_chunk_key
                UNIQUE (corpus_label, doc_sha256, chunk_index);
                """
            )

    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS rag_chunks_doc_path_idx
            ON rag_chunks (doc_path);
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS rag_chunks_corpus_label_idx
            ON rag_chunks (corpus_label);
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS rag_chunks_meta_gin_idx
            ON rag_chunks USING GIN (meta);
            """
        )
    conn.commit()


def set_meta_if_absent(conn: psycopg.Connection, key: str, value: str) -> None:
    """note: Writes a rag_meta value only if the key does not already exist."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO rag_meta (k, v) VALUES (%s, %s)
            ON CONFLICT (k) DO NOTHING;
            """,
            (key, value),
        )
    conn.commit()


def set_meta(conn: psycopg.Connection, key: str, value: str) -> None:
    """note: Writes a rag_meta value unconditionally, overwriting any existing value."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO rag_meta (k, v) VALUES (%s, %s)
            ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v, updated_at = now();
            """,
            (key, value),
        )
    conn.commit()


def get_meta(conn: psycopg.Connection, key: str) -> str | None:
    """note: Retrieves a rag_meta value by key (or None if missing)."""
    with conn.cursor() as cur:
        cur.execute("SELECT v FROM rag_meta WHERE k = %s;", (key,))
        row = cur.fetchone()
        return str(row[0]) if row else None


def chunks_rowcount(conn: psycopg.Connection, corpus_label: str = "") -> int:
    """note: Returns the number of stored rag_chunks rows for a corpus_label ('' = all rows)."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.rag_chunks') IS NOT NULL;")
        exists = bool(cur.fetchone()[0])
        if not exists:
            return 0
        if corpus_label:
            cur.execute("SELECT COUNT(*) FROM rag_chunks WHERE corpus_label = %s;", (corpus_label,))
        else:
            cur.execute("SELECT COUNT(*) FROM rag_chunks;")
        return int(cur.fetchone()[0])


def clear_chunks(conn: psycopg.Connection) -> int:
    """note: Deletes ALL rows from rag_chunks (all corpora) and returns the number deleted."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.rag_chunks') IS NOT NULL;")
        exists = bool(cur.fetchone()[0])
        if not exists:
            return 0
        cur.execute("DELETE FROM rag_chunks;")
        deleted = cur.rowcount if cur.rowcount is not None else 0
    conn.commit()
    return int(deleted)


def clear_corpus(conn: psycopg.Connection, corpus_label: str) -> int:
    """note: Deletes only rows belonging to corpus_label and returns the number deleted."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.rag_chunks') IS NOT NULL;")
        exists = bool(cur.fetchone()[0])
        if not exists:
            return 0
        cur.execute("DELETE FROM rag_chunks WHERE corpus_label = %s;", (corpus_label,))
        deleted = cur.rowcount if cur.rowcount is not None else 0
    conn.commit()
    return int(deleted)


def _vector_literal(vec: list[float]) -> str:
    """note: Formats a Python list[float] as a pgvector literal for safe casting."""
    return "[" + ",".join(f"{float(x):.10g}" for x in vec) + "]"


def upsert_chunks(
    conn: psycopg.Connection,
    rows: Iterable[dict[str, Any]],
) -> int:
    """note: Upserts chunk rows keyed by (corpus_label, doc_sha256, chunk_index); returns row count."""
    sql = """
    INSERT INTO rag_chunks (
        corpus_label, doc_path, doc_sha256, chunk_index, chunk_text, embedding, meta
    ) VALUES (
        %(corpus_label)s, %(doc_path)s, %(doc_sha256)s, %(chunk_index)s, %(chunk_text)s,
        %(embedding)s::vector, %(meta)s::jsonb
    )
    ON CONFLICT (corpus_label, doc_sha256, chunk_index)
    DO UPDATE SET
        doc_path = EXCLUDED.doc_path,
        chunk_text = EXCLUDED.chunk_text,
        embedding = EXCLUDED.embedding,
        meta = EXCLUDED.meta,
        updated_at = now();
    """
    count = 0
    with conn.cursor() as cur:
        for r in rows:
            rr = dict(r)
            rr.setdefault("corpus_label", "")
            rr["meta"] = Json(rr.get("meta") or {})
            rr["embedding"] = _vector_literal(rr["embedding"])
            cur.execute(sql, rr)
            count += 1
    conn.commit()
    return count


def similarity_search(
    conn: psycopg.Connection,
    query_embedding: list[float],
    top_k: int,
    corpus_label: str = "",
) -> list[dict[str, Any]]:
    """note: Retrieves top-k chunks by vector distance using pgvector (<->); optionally filtered by corpus_label."""
    qv = _vector_literal(query_embedding)
    with conn.cursor() as cur:
        if corpus_label:
            cur.execute(
                """
                SELECT doc_path, chunk_index, chunk_text, meta, (embedding <-> %s::vector) AS distance
                FROM rag_chunks
                WHERE corpus_label = %s
                ORDER BY embedding <-> %s::vector
                LIMIT %s;
                """,
                (qv, corpus_label, qv, int(top_k)),
            )
        else:
            cur.execute(
                """
                SELECT doc_path, chunk_index, chunk_text, meta, (embedding <-> %s::vector) AS distance
                FROM rag_chunks
                ORDER BY embedding <-> %s::vector
                LIMIT %s;
                """,
                (qv, qv, int(top_k)),
            )
        rows = cur.fetchall() or []
    out: list[dict[str, Any]] = []
    for doc_path, chunk_index, chunk_text, meta, distance in rows:
        out.append(
            {
                "doc_path": str(doc_path),
                "chunk_index": int(chunk_index),
                "chunk_text": str(chunk_text),
                "meta": meta,
                "distance": float(distance) if distance is not None else None,
            }
        )
    return out


def get_random_chunks(conn: psycopg.Connection, n: int = 1, corpus_label: str = "") -> list[dict[str, Any]]:
    """note: Returns n arbitrary chunk rows for seeding generation; optionally filtered by corpus_label."""
    with conn.cursor() as cur:
        if corpus_label:
            cur.execute(
                """
                SELECT doc_path, chunk_index, chunk_text, meta
                FROM rag_chunks
                WHERE corpus_label = %s
                ORDER BY random()
                LIMIT %s;
                """,
                (corpus_label, int(n)),
            )
        else:
            cur.execute(
                """
                SELECT doc_path, chunk_index, chunk_text, meta
                FROM rag_chunks
                ORDER BY random()
                LIMIT %s;
                """,
                (int(n),),
            )
        rows = cur.fetchall() or []
    out = []
    for doc_path, chunk_index, chunk_text, meta in rows:
        out.append(
            {
                "doc_path": str(doc_path),
                "chunk_index": int(chunk_index),
                "chunk_text": str(chunk_text),
                "meta": meta,
            }
        )
    return out


def get_db_snapshot_summary(conn: psycopg.Connection, corpus_label: str = "") -> dict[str, Any]:
    """note: Returns aggregate statistics over rag_chunks for DB Snapshot sheet.

    If corpus_label is given, counts are scoped to that corpus only.
    """
    from datetime import datetime, timezone

    snapshot_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    summary: dict[str, Any] = {
        "snapshot_taken_at": snapshot_at,
        "corpus_label": corpus_label or "(all)",
    }

    # rag_meta — read all keys
    with conn.cursor() as cur:
        cur.execute("SELECT k, v FROM rag_meta ORDER BY k;")
        for k, v in (cur.fetchall() or []):
            summary[f"rag_meta.{k}"] = str(v)

    # rag_chunks aggregate
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.rag_chunks') IS NOT NULL;")
        table_exists = bool(cur.fetchone()[0])

    if not table_exists:
        summary["chunks_total"] = 0
        summary["distinct_docs"] = 0
        summary["distinct_doc_sha256s"] = 0
        summary["oldest_chunk_created_at"] = None
        summary["newest_chunk_updated_at"] = None
        return summary

    with conn.cursor() as cur:
        if corpus_label:
            cur.execute(
                """
                SELECT
                    COUNT(*)                        AS chunks_total,
                    COUNT(DISTINCT doc_path)        AS distinct_docs,
                    COUNT(DISTINCT doc_sha256)      AS distinct_doc_sha256s,
                    MIN(created_at)                 AS oldest_chunk_created_at,
                    MAX(updated_at)                 AS newest_chunk_updated_at
                FROM rag_chunks
                WHERE corpus_label = %s;
                """,
                (corpus_label,),
            )
        else:
            cur.execute(
                """
                SELECT
                    COUNT(*)                        AS chunks_total,
                    COUNT(DISTINCT doc_path)        AS distinct_docs,
                    COUNT(DISTINCT doc_sha256)      AS distinct_doc_sha256s,
                    MIN(created_at)                 AS oldest_chunk_created_at,
                    MAX(updated_at)                 AS newest_chunk_updated_at
                FROM rag_chunks;
                """
            )
        row = cur.fetchone()

    if row:
        summary["chunks_total"] = int(row[0]) if row[0] is not None else 0
        summary["distinct_docs"] = int(row[1]) if row[1] is not None else 0
        summary["distinct_doc_sha256s"] = int(row[2]) if row[2] is not None else 0
        summary["oldest_chunk_created_at"] = str(row[3]) if row[3] is not None else None
        summary["newest_chunk_updated_at"] = str(row[4]) if row[4] is not None else None

    return summary


def get_db_snapshot_per_doc(conn: psycopg.Connection, corpus_label: str = "") -> list[dict[str, Any]]:
    """note: Returns one row per distinct doc_path with chunk count, sha256, and timestamps.

    If corpus_label is given, scoped to that corpus only.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.rag_chunks') IS NOT NULL;")
        if not bool(cur.fetchone()[0]):
            return []

    with conn.cursor() as cur:
        if corpus_label:
            cur.execute(
                """
                SELECT
                    doc_path,
                    COUNT(*)                   AS chunk_count,
                    MAX(doc_sha256)            AS doc_sha256,
                    MIN(created_at)            AS first_created_at,
                    MAX(updated_at)            AS last_updated_at
                FROM rag_chunks
                WHERE corpus_label = %s
                GROUP BY doc_path
                ORDER BY doc_path;
                """,
                (corpus_label,),
            )
        else:
            cur.execute(
                """
                SELECT
                    doc_path,
                    COUNT(*)                   AS chunk_count,
                    MAX(doc_sha256)            AS doc_sha256,
                    MIN(created_at)            AS first_created_at,
                    MAX(updated_at)            AS last_updated_at
                FROM rag_chunks
                GROUP BY doc_path
                ORDER BY doc_path;
                """
            )
        rows = cur.fetchall() or []

    out: list[dict[str, Any]] = []
    for doc_path, chunk_count, doc_sha256, first_created, last_updated in rows:
        out.append(
            {
                "doc_path": str(doc_path),
                "chunk_count": int(chunk_count),
                "doc_sha256": str(doc_sha256),
                "first_created_at": str(first_created) if first_created is not None else None,
                "last_updated_at": str(last_updated) if last_updated is not None else None,
            }
        )
    return out
