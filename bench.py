#!/usr/bin/env python3
"""
bench.py — Benchmark script for CP5/CP6.

Reads .md files from data/hoc-bong-chon-loc/, parses YAML frontmatter,
chunks the body, loads into EmbeddingStore, and runs 5 benchmark queries.

Strategy: recursive_280 (RecursiveChunker, chunk_size=280)
Author:   Trần Hồng Sơn — K4-L3A / Nhóm G15
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.agent import KnowledgeBaseAgent
from src.chunking import RecursiveChunker, SentenceChunker, FixedSizeChunker
from src.embeddings import (
    EMBEDDING_PROVIDER_ENV,
    GEMINI_EMBEDDING_MODEL,
    LOCAL_EMBEDDING_MODEL,
    OPENAI_EMBEDDING_MODEL,
    GeminiEmbedder,
    LocalEmbedder,
    OpenAIEmbedder,
    _mock_embed,
)
from src.models import Document
from src.store import EmbeddingStore


# ── Data directory ──────────────────────────────────────────────────────
DATA_DIR = Path("data/hoc-bong-chon-loc")


# ── Custom chunkers (team strategies) ──────────────────────────────────
class HeadingChunker:
    """Split by Markdown headings; re-attach heading to sub-chunks."""

    def __init__(self, chunk_size: int = 320) -> None:
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        sections = re.split(r"(?=^#{1,3} )", text, flags=re.MULTILINE)
        chunks: list[str] = []
        for section in sections:
            section = section.strip()
            if not section:
                continue
            if len(section) <= self.chunk_size:
                chunks.append(section)
            else:
                lines = section.split("\n", 1)
                heading = lines[0] if len(lines) > 1 else ""
                body = lines[1] if len(lines) > 1 else section
                for part in RecursiveChunker(chunk_size=self.chunk_size - len(heading) - 1).chunk(body):
                    chunks.append(f"{heading}\n{part}" if heading else part)
        return chunks


class ParagraphChunker:
    """Merge adjacent paragraphs up to chunk_size."""

    def __init__(self, chunk_size: int = 360) -> None:
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        paragraphs = re.split(r"\n{2,}", text.strip())
        chunks: list[str] = []
        current = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if current and len(current) + 2 + len(para) <= self.chunk_size:
                current += "\n\n" + para
            else:
                if current:
                    chunks.append(current)
                if len(para) <= self.chunk_size:
                    current = para
                else:
                    for sub in RecursiveChunker(chunk_size=self.chunk_size).chunk(para):
                        chunks.append(sub)
                    current = ""
        if current:
            chunks.append(current)
        return chunks


# ── Frontmatter parser ─────────────────────────────────────────────────
def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from a markdown file. Returns (metadata, body)."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            meta: dict = {}
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    key, _, val = line.partition(":")
                    meta[key.strip()] = val.strip()
            return meta, parts[2].strip()
    return {}, text.strip()


# ── Chunking strategy selector ─────────────────────────────────────────
STRATEGY = os.getenv("BENCH_STRATEGY", "recursive_280")


def get_chunker(strategy: str = STRATEGY):
    """Return a chunker instance based on strategy name."""
    strategies = {
        "fixed_220":      lambda: FixedSizeChunker(chunk_size=220, overlap=30),
        "sentence_2":     lambda: SentenceChunker(max_sentences_per_chunk=2),
        "recursive_280":  lambda: RecursiveChunker(chunk_size=280),
        "heading_320":    lambda: HeadingChunker(chunk_size=320),
        "paragraph_360":  lambda: ParagraphChunker(chunk_size=360),
    }
    factory = strategies.get(strategy)
    if factory is None:
        print(f"Unknown strategy '{strategy}', falling back to sentence_2")
        return SentenceChunker(max_sentences_per_chunk=2)
    return factory()


# ── 5 benchmark queries ────────────────────────────────────────────────
QUERIES = [
    {
        "id": "Q1",
        "query": "Học bổng President's Excellence của VinUni chi trả những gì?",
        "gold_answer": "Toàn bộ học phí và chi phí sinh hoạt.",
        "gold_doc_id": "undergraduate-scholarships",
        "marker": "chi phí sinh hoạt",
        "metadata_filter": None,
    },
    {
        "id": "Q2",
        "query": "Sinh viên VinUni cần GPA tối thiểu bao nhiêu để duy trì học bổng 100%?",
        "gold_answer": "GPA tích lũy của năm xét ít nhất 3,2.",
        "gold_doc_id": "scholarship-renewal-policy",
        "marker": "3,2",
        "metadata_filter": None,
    },
    {
        "id": "Q3",
        "query": "Ở UET, học bổng loại Giỏi cho khóa QH-2023 đến QH-2025 là bao nhiêu mỗi tháng?",
        "gold_answer": "3.500.000đ/tháng.",
        "gold_doc_id": "uet-merit-scholarship-2025-2026",
        "marker": "3.500.000",
        "metadata_filter": None,
    },
    {
        "id": "Q4",
        "query": "Sinh viên RMIT Việt Nam đang học cần bao nhiêu tín chỉ và GPA để xin học bổng thành tích 2026?",
        "gold_answer": "Ít nhất 96 tín chỉ tại RMIT Việt Nam và GPA tích lũy 3,4/4,0.",
        "gold_doc_id": "rmit-current-student-scholarship-2026",
        "marker": "96",
        "metadata_filter": None,
    },
    {
        "id": "Q5",
        "query": "Ở UEH, mức hỗ trợ tài chính tối đa cho một học kỳ là bao nhiêu?",
        "gold_answer": "Học bổng toàn phần cho sinh viên bằng 100% học phí trung bình của 15 tín chỉ.",
        "gold_doc_id": "ueh-learning-support-scholarship",
        "marker": "15 tín chỉ",
        "metadata_filter": {"audience": "student"},
    },
]


def make_embedder():
    """Build embedding function based on .env, fallback to mock."""
    load_dotenv(override=False)
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower()
    if provider == "local":
        try:
            return LocalEmbedder(model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL))
        except Exception:
            pass
    elif provider == "openai":
        try:
            return OpenAIEmbedder(model_name=os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL))
        except Exception:
            pass
    elif provider == "gemini":
        try:
            return GeminiEmbedder(model_name=os.getenv("GEMINI_EMBEDDING_MODEL", GEMINI_EMBEDDING_MODEL))
        except Exception:
            pass
    return _mock_embed


def simple_llm(prompt: str) -> str:
    """Extract first line from context that contains key information."""
    lines = prompt.split("\n")
    for line in lines:
        line = line.strip()
        if line and not line.startswith(("Dựa trên", "Chỉ sử dụng", "Trích dẫn", "Nếu không",
                                         "Ngữ cảnh:", "Câu hỏi:", "Trả lời:", "[", "---")):
            if len(line) > 30:
                return line
    return "Không tìm thấy câu trả lời trong ngữ cảnh được cung cấp."


# ── Main ───────────────────────────────────────────────────────────────
def main() -> int:
    strategy = os.getenv("BENCH_STRATEGY", STRATEGY)
    chunker = get_chunker(strategy)
    embedder = make_embedder()
    backend_name = getattr(embedder, "_backend_name", embedder.__class__.__name__)

    output_lines: list[str] = []

    def log(msg: str = "") -> None:
        print(msg)
        output_lines.append(msg)

    log(f"=== Benchmark: strategy={strategy}, embedding={backend_name} ===")
    log()

    # 1. Read and parse all .md files
    md_files = sorted(DATA_DIR.glob("*.md"))
    if not md_files:
        log(f"ERROR: No .md files found in {DATA_DIR}")
        return 1

    # 2. Chunk and create Documents
    all_docs: list[Document] = []
    for md_path in md_files:
        text = md_path.read_text(encoding="utf-8")
        metadata, body = parse_frontmatter(text)
        if not body.strip():
            log(f"  SKIP (empty body): {md_path.name}")
            continue

        doc_id = metadata.get("doc_id", md_path.stem)
        chunks = chunker.chunk(body)
        log(f"  {md_path.name}: {len(chunks)} chunks (doc_id={doc_id})")

        for i, chunk_text in enumerate(chunks):
            all_docs.append(
                Document(
                    id=f"{doc_id}#{i}",
                    content=chunk_text,
                    metadata={**metadata, "doc_id": doc_id},
                )
            )

    log(f"\nTotal chunks loaded: {len(all_docs)}")
    log()

    # 3. Load into store
    store = EmbeddingStore(collection_name="bench", embedding_fn=embedder)
    store.add_documents(all_docs)
    log(f"Store size: {store.get_collection_size()}")
    log()

    # 4. Run queries
    agent = KnowledgeBaseAgent(store=store, llm_fn=simple_llm)
    total_score = 0

    for q in QUERIES:
        log(f"--- {q['id']}: {q['query']} ---")
        log(f"Gold: {q['gold_answer']}  (doc: {q['gold_doc_id']})")

        if q["metadata_filter"]:
            results = store.search_with_filter(q["query"], top_k=3, metadata_filter=q["metadata_filter"])
            log(f"Filter: {q['metadata_filter']}")
        else:
            results = store.search(q["query"], top_k=3)

        # Score
        score = 0
        for rank, r in enumerate(results, 1):
            is_gold = r["metadata"].get("doc_id") == q["gold_doc_id"]
            has_marker = q["marker"] in r["content"]
            tag = ""
            if is_gold and has_marker:
                tag = " ★ GOLD+MARKER"
                if rank == 1 and score < 2:
                    score = 2
                elif score < 1:
                    score = 1
            elif is_gold:
                tag = " ☆ GOLD"
                if score < 1:
                    score = 1
            log(f"  top-{rank}: score={r['score']:.4f}  doc_id={r['metadata'].get('doc_id')}  "
                f"id={r['id']}{tag}")
            log(f"         {r['content'][:120].replace(chr(10), ' ')}")

        # A/B test for Q5: also run without filter
        if q["metadata_filter"]:
            log(f"\n  A/B (no filter):")
            results_nofilter = store.search(q["query"], top_k=3)
            for rank, r in enumerate(results_nofilter, 1):
                is_gold = r["metadata"].get("doc_id") == q["gold_doc_id"]
                tag = " ★ GOLD" if is_gold else ""
                log(f"  top-{rank}: score={r['score']:.4f}  doc_id={r['metadata'].get('doc_id')}{tag}")

        # Agent answer
        answer = agent.answer(q["query"], top_k=3)
        log(f"\n  Agent: {answer[:200]}")
        log(f"  Score: {score}/2")
        total_score += score
        log()

    log(f"=== Total score: {total_score}/10 ===")

    # Write output
    output_path = Path("ket_qua_benchmark.txt")
    output_path.write_text("\n".join(output_lines), encoding="utf-8")
    print(f"\nOutput written to {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
