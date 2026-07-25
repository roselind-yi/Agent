from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]")


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    content: str
    tags: list[str]


@dataclass(frozen=True)
class SearchHit:
    document: Document
    score: float


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def cosine_similarity(left: Counter[str], right: Counter[str]) -> float:
    common = set(left) & set(right)
    numerator = sum(left[token] * right[token] for token in common)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


class LocalVectorStore:
    """Small persistent retriever used when ChromaDB is not installed."""

    def __init__(self, documents: Iterable[Document]):
        self.documents = list(documents)
        self._vectors = {
            doc.id: Counter(tokenize(" ".join([doc.title, doc.content, " ".join(doc.tags)])))
            for doc in self.documents
        }

    @classmethod
    def from_json(cls, path: Path) -> "LocalVectorStore":
        payload = json.loads(path.read_text(encoding="utf-8"))
        documents = [
            Document(
                id=item["id"],
                title=item["title"],
                content=item["content"],
                tags=item.get("tags", []),
            )
            for item in payload["documents"]
        ]
        return cls(documents)

    def search(self, query: str, top_k: int = 3) -> list[SearchHit]:
        query_vector = Counter(tokenize(query))
        hits = [
            SearchHit(document=doc, score=cosine_similarity(query_vector, self._vectors[doc.id]))
            for doc in self.documents
        ]
        ranked = sorted(hits, key=lambda hit: hit.score, reverse=True)
        return [hit for hit in ranked[:top_k] if hit.score > 0]

    def add_document(self, document: Document) -> None:
        self.documents.append(document)
        self._vectors[document.id] = Counter(tokenize(document.title + " " + document.content))


class ChromaVectorStore:
    """Optional adapter; activated only when chromadb is available."""

    def __init__(self, persist_directory: Path, collection_name: str = "journey_knowledge"):
        import chromadb  # type: ignore

        self._client = chromadb.PersistentClient(path=str(persist_directory))
        self._collection = self._client.get_or_create_collection(collection_name)

    def upsert(self, documents: Iterable[Document]) -> None:
        docs = list(documents)
        if not docs:
            return
        self._collection.upsert(
            ids=[doc.id for doc in docs],
            documents=[doc.content for doc in docs],
            metadatas=[{"title": doc.title, "tags": ",".join(doc.tags)} for doc in docs],
        )

    def search(self, query: str, top_k: int = 3) -> list[SearchHit]:
        result = self._collection.query(query_texts=[query], n_results=top_k)
        hits: list[SearchHit] = []
        ids = result.get("ids", [[]])[0]
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        for idx, doc_id in enumerate(ids):
            meta = metas[idx] or {}
            distance = distances[idx] if idx < len(distances) else 1
            hits.append(
                SearchHit(
                    document=Document(
                        id=doc_id,
                        title=meta.get("title", doc_id),
                        content=docs[idx],
                        tags=str(meta.get("tags", "")).split(",") if meta.get("tags") else [],
                    ),
                    score=max(0.0, 1.0 - float(distance)),
                )
            )
        return hits

