"""Persistence adapters for validated ResearchGraph objects."""

from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path
from typing import List

from .research_graph import ResearchEdge, ResearchGraph, ResearchNode, ResearchNodeType


class SQLiteResearchGraphStore:
    """Small local graph store using stdlib SQLite.

    This is intentionally simple and dependency-free. It provides a durable local
    substrate before optional Kuzu/Cognee integrations are added.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def write_graph(self, graph: ResearchGraph, replace: bool = False) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as con:
            self._ensure_schema(con)
            if replace:
                con.execute("delete from edges")
                con.execute("delete from nodes")
            for node in graph.nodes:
                con.execute(
                    """
                    insert or replace into nodes
                    (id, name, type, aliases_json, description, source_path, metadata_json)
                    values (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        node.id,
                        node.name,
                        node.type.value,
                        json.dumps(node.aliases, ensure_ascii=False),
                        node.description,
                        node.source_path,
                        json.dumps(node.metadata, ensure_ascii=False, sort_keys=True),
                    ),
                )
            for edge in graph.edges:
                edge_id = f"{edge.source}|{edge.type}|{edge.target}"
                con.execute(
                    """
                    insert or replace into edges
                    (id, source, target, type, evidence, metadata_json)
                    values (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        edge_id,
                        edge.source,
                        edge.target,
                        edge.type,
                        edge.evidence,
                        json.dumps(edge.metadata, ensure_ascii=False, sort_keys=True),
                    ),
                )
            con.commit()

    def read_graph(self) -> ResearchGraph:
        with sqlite3.connect(self.path) as con:
            self._ensure_schema(con)
            nodes = [
                ResearchNode(
                    id=row[0],
                    name=row[1],
                    type=ResearchNodeType(row[2]),
                    aliases=json.loads(row[3] or "[]"),
                    description=row[4] or "",
                    source_path=row[5],
                    metadata=json.loads(row[6] or "{}"),
                )
                for row in con.execute("select id, name, type, aliases_json, description, source_path, metadata_json from nodes order by rowid")
            ]
            edges = [
                ResearchEdge(
                    source=row[0],
                    target=row[1],
                    type=row[2],
                    evidence=row[3],
                    metadata=json.loads(row[4] or "{}"),
                )
                for row in con.execute("select source, target, type, evidence, metadata_json from edges order by rowid")
            ]
            return ResearchGraph(nodes=nodes, edges=edges)

    def _ensure_schema(self, con: sqlite3.Connection) -> None:
        con.execute(
            """
            create table if not exists nodes (
                id text primary key,
                name text not null,
                type text not null,
                aliases_json text not null,
                description text not null,
                source_path text,
                metadata_json text not null
            )
            """
        )
        con.execute("create index if not exists idx_nodes_type on nodes(type)")
        con.execute("create index if not exists idx_nodes_name on nodes(name)")
        con.execute(
            """
            create table if not exists edges (
                id text primary key,
                source text not null,
                target text not null,
                type text not null,
                evidence text,
                metadata_json text not null,
                foreign key(source) references nodes(id),
                foreign key(target) references nodes(id)
            )
            """
        )
        con.execute("create index if not exists idx_edges_type on edges(type)")
        con.execute("create index if not exists idx_edges_source on edges(source)")
        con.execute("create index if not exists idx_edges_target on edges(target)")


class KuzuResearchGraphStore:
    """Kuzu graph store for validated ResearchGraph objects."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def write_graph(self, graph: ResearchGraph, replace: bool = False) -> None:
        kuzu = import_kuzu()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if replace and self.path.exists():
            if self.path.is_dir():
                shutil.rmtree(self.path)
            else:
                self.path.unlink()
        db = kuzu.Database(str(self.path))
        con = kuzu.Connection(db)
        self._ensure_schema(con)
        if replace:
            # Re-created database is already empty; this branch exists for API symmetry.
            pass
        for node in graph.nodes:
            con.execute(
                "CREATE (:Node {id: $id, name: $name, type: $type, aliases_json: $aliases_json, description: $description, source_path: $source_path, metadata_json: $metadata_json})",
                {
                    "id": node.id,
                    "name": node.name,
                    "type": node.type.value,
                    "aliases_json": json.dumps(node.aliases, ensure_ascii=False),
                    "description": node.description,
                    "source_path": node.source_path or "",
                    "metadata_json": json.dumps(node.metadata, ensure_ascii=False, sort_keys=True),
                },
            )
        for edge in graph.edges:
            con.execute(
                """
                MATCH (a:Node {id: $source}), (b:Node {id: $target})
                CREATE (a)-[:Edge {type: $type, evidence: $evidence, metadata_json: $metadata_json}]->(b)
                """,
                {
                    "source": edge.source,
                    "target": edge.target,
                    "type": edge.type,
                    "evidence": edge.evidence or "",
                    "metadata_json": json.dumps(edge.metadata, ensure_ascii=False, sort_keys=True),
                },
            )

    def read_graph(self) -> ResearchGraph:
        kuzu = import_kuzu()
        db = kuzu.Database(str(self.path), read_only=True)
        con = kuzu.Connection(db)
        nodes = []
        result = con.execute("MATCH (n:Node) RETURN n.id, n.name, n.type, n.aliases_json, n.description, n.source_path, n.metadata_json ORDER BY n.id")
        while result.has_next():
            row = result.get_next()
            nodes.append(
                ResearchNode(
                    id=row[0],
                    name=row[1],
                    type=ResearchNodeType(row[2]),
                    aliases=json.loads(row[3] or "[]"),
                    description=row[4] or "",
                    source_path=row[5] or None,
                    metadata=json.loads(row[6] or "{}"),
                )
            )
        edges = []
        result = con.execute("MATCH (a:Node)-[e:Edge]->(b:Node) RETURN a.id, b.id, e.type, e.evidence, e.metadata_json ORDER BY a.id, e.type, b.id")
        while result.has_next():
            row = result.get_next()
            edges.append(
                ResearchEdge(
                    source=row[0],
                    target=row[1],
                    type=row[2],
                    evidence=row[3] or None,
                    metadata=json.loads(row[4] or "{}"),
                )
            )
        return ResearchGraph(nodes=nodes, edges=edges)

    def counts(self) -> dict:
        kuzu = import_kuzu()
        db = kuzu.Database(str(self.path), read_only=True)
        con = kuzu.Connection(db)
        node_count = con.execute("MATCH (n:Node) RETURN count(n)").get_next()[0]
        edge_count = con.execute("MATCH (:Node)-[e:Edge]->(:Node) RETURN count(e)").get_next()[0]
        return {"nodes": node_count, "edges": edge_count}

    def _ensure_schema(self, con) -> None:
        con.execute(
            """
            CREATE NODE TABLE IF NOT EXISTS Node(
                id STRING,
                name STRING,
                type STRING,
                aliases_json STRING,
                description STRING,
                source_path STRING,
                metadata_json STRING,
                PRIMARY KEY(id)
            )
            """
        )
        con.execute("CREATE REL TABLE IF NOT EXISTS Edge(FROM Node TO Node, type STRING, evidence STRING, metadata_json STRING)")


def import_kuzu():
    try:
        import kuzu
    except ImportError as exc:
        raise RuntimeError("kuzu is not installed. Install it with: python3 -m pip install --user kuzu") from exc
    return kuzu
