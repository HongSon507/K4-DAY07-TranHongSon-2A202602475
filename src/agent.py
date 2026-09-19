from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        # Handle empty store — don't crash, don't call LLM needlessly
        if self.store.get_collection_size() == 0:
            return "Không tìm thấy tài liệu nào trong cơ sở tri thức."

        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy tài liệu liên quan đến câu hỏi."

        # Build numbered context for source traceability
        context_parts: list[str] = []
        for i, r in enumerate(results, 1):
            source = r.get("metadata", {}).get("source_url", "unknown")
            context_parts.append(f"[{i}] (source: {source})\n{r['content']}")
        context = "\n\n".join(context_parts)

        prompt = (
            "Dựa trên ngữ cảnh bên dưới, hãy trả lời câu hỏi. "
            "Chỉ sử dụng thông tin từ ngữ cảnh được cung cấp. "
            "Trích dẫn số nguồn [1], [2], ... khi trả lời. "
            "Nếu không tìm thấy câu trả lời trong ngữ cảnh, hãy nói rõ.\n\n"
            f"Ngữ cảnh:\n{context}\n\n"
            f"Câu hỏi: {question}\n\n"
            "Trả lời:"
        )

        return self.llm_fn(prompt)

