# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Hồng Sơn
**Mã SV:** 2A202602475
**Nhóm:** G15
**Ngày:** 19/09/2026


---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao (giá trị tiến gần về 1) biểu thị rằng hai vector embedding tạo với nhau một góc rất nhỏ trong không gian vector nhiều chiều. Về mặt ngôn ngữ, điều này phản ánh hai đoạn văn bản có mức độ tương đồng ngữ nghĩa lớn hoặc cùng hướng ngữ cảnh trọng tâm, bất kể độ dài hay số lượng từ giữa chúng có thể khác biệt.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên có hoàn cảnh kinh tế khó khăn được nhà trường xét cấp học bổng hỗ trợ học tập."
- Câu B: "Chính sách trợ cấp tài chính dành cho người học có hoàn cảnh gia đình đặc biệt khó khăn."
- Tại sao tương đồng: Dù sử dụng các từ vựng khác nhau (sinh viên / người học, hỗ trợ học bổng / trợ cấp tài chính, khó khăn / đặc biệt khó khăn), cả hai câu đều mang cùng một thông điệp cốt lõi và ngữ cảnh ngữ nghĩa về chính sách hỗ trợ tài chính cho người học.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "VinUni cấp học bổng toàn phần chi trả toàn bộ học phí và sinh hoạt phí cho sinh viên."
- Câu B: "Hôm nay thời tiết Hà Nội nhiều mây và có thể có mưa rào rải rác vào buổi chiều."
- Tại sao khác: Hai câu thuộc hai miền chủ đề hoàn toàn độc lập và không liên quan đến nhau (chính sách học bổng đại học đối chiếu với bản tin dự báo thời tiết), không chia sẻ bất kỳ đặc trưng ngữ nghĩa hay bối cảnh chung nào.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity chỉ đo góc giữa hai vector mà độc lập với độ lớn (magnitude/norm), tức không bị ảnh hưởng bởi độ dài của văn bản (một câu ngắn và một đoạn văn dài cùng nội dung vẫn có cosine similarity cao). Ngược lại, khoảng cách Euclid bị chi phối bởi độ dài vector, khiến các văn bản cùng ý nghĩa nhưng khác độ dài bị xem là rất xa nhau trong không gian biểu diễn.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> - Bước trượt (stride): $\text{step} = \text{chunk\_size} - \text{overlap} = 500 - 50 = 450$ ký tự.
> - Chunk đầu tiên bao phủ đoạn từ ký tự $0$ đến $500$.
> - Phần văn bản còn lại cần bao phủ: $10.000 - 500 = 9.500$ ký tự.
> - Số chunk bổ sung cần trượt: $\lceil 9.500 / 450 \rceil = \lceil 21,11 \rceil = 22$ chunks.
> - Tổng số chunk được tạo ra: $1 + 22 = 23$ chunks (hoặc tính theo công thức trượt: $\lceil (10.000 - 50) / 450 \rceil = \lceil 9.950 / 450 \rceil = 23$ chunks).
> *Đáp án:* **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> - *Thay đổi số lượng chunk:* Bước trượt giảm còn $500 - 100 = 400$ ký tự. Số chunk tăng lên thành $1 + \lceil 9.500 / 400 \rceil = 1 + 24 = 25$ chunks (tăng thêm 2 chunks so với mức overlap 50).
> - *Lý do muốn độ chồng chéo nhiều hơn:* Tăng overlap giúp giảm thiểu tối đa hiện tượng đứt gãy ngữ cảnh (context fragmentation) tại các điểm ranh giới chia cắt (như câu văn quan trọng, điều kiện học bổng, bảng biểu bị cắt ngang giữa hai chunk), từ đó giúp retriever tìm được đầy đủ ngữ cảnh hoàn chỉnh hơn khi truy vấn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
Sử dụng biểu thức chính quy `re.split(r"(?<=[.!?])(?:\s+|\n+)", text.strip())` với positive lookbehind để tách câu mà vẫn giữ nguyên dấu câu kết thúc (`.`, `!`, `?`). Xử lý chặt chẽ các edge cases: chuỗi rỗng/chỉ chứa khoảng trắng trả về `[]`, văn bản không có dấu câu thì giữ nguyên, và gom tuần tự tối đa `max_sentences_per_chunk` câu vào mỗi chunk đồng thời dùng `strip()` loại bỏ khoảng trắng thừa.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
Thuật toán hoạt động theo hai chiều: đệ quy xuống sâu (mảnh nào dài hơn `chunk_size` thì gọi tiếp `_split` với separator nhỏ hơn kế tiếp) và gom lên (nối các mảnh nhỏ liền kề bằng separator hiện tại cho đến sát `chunk_size` để tránh sinh chunk vụn). Có 3 base cases xử lý dừng: (1) chuỗi rỗng trả về `[]`, (2) độ dài chuỗi `<= chunk_size` trả về `[text]`, và (3) danh sách separator rỗng hoặc không còn separator nào khớp trong chuỗi thì phân tách dự phòng (fallback) theo lát cắt cố định độ dài `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
Bỏ hẳn nhánh ChromaDB (cái bẫy trong scaffolding), chỉ dùng in-memory `list[dict]`. Mỗi `Document` được chuẩn hoá qua `_make_record` thành dict chứa `id`, `content`, `metadata` (copy, có thêm khoá `doc_id`), và `embedding`. Khi `search`, embed query rồi tính dot product với từng record, sắp xếp giảm dần và trả top-k (loại bỏ vector ra khỏi kết quả để output sạch).

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
`search_with_filter` lọc **trước** rồi mới search — nếu lọc sau thì top-k slots bị chiếm bởi tài liệu không khớp filter, có thể trả 0 kết quả dù store vẫn còn tài liệu hợp lệ. `delete_document` dùng list comprehension loại bỏ mọi record có `metadata['doc_id']` khớp, trả `True`/`False` tuỳ có xoá được gì không.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
RAG 3 nhịp: (1) truy xuất top-k chunks từ store, (2) dựng prompt có ngữ cảnh đánh số `[1]`, `[2]`, `[3]` kèm source URL để truy vết nguồn, yêu cầu model chỉ dùng ngữ cảnh và trích dẫn số nguồn, (3) gọi `llm_fn`. Xử lý trường hợp store rỗng hoặc không tìm thấy kết quả — trả thông báo thay vì crash.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.10s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Học bổng VinUni chi trả toàn bộ học phí và sinh hoạt phí. | Sinh viên xuất sắc được VinUni tài trợ 100% học phí và tiền sinh hoạt. | cao | 0.0871 | Không (do Mock Embedder băm MD5) |
| 2 | Sinh viên cần duy trì GPA tối thiểu 3.2 để không bị mất học bổng. | Điều kiện duy trì học bổng toàn phần là điểm trung bình tích lũy đạt từ 3.2 trở lên. | cao | -0.0644 | Không |
| 3 | Học bổng VinUni chi trả toàn bộ học phí và sinh hoạt phí. | Hôm nay thời tiết Hà Nội nhiều mây và có thể có mưa rào rải rác. | thấp | -0.2134 | Đúng |
| 4 | Quy định xét cấp học bổng khuyến khích học tập tại Đại học Công nghệ. | Học bổng khuyến khích UET dành cho sinh viên có kết quả học tập và rèn luyện tốt. | cao | -0.0280 | Không |
| 5 | Mức hỗ trợ tài chính tối đa cho sinh viên UEH là 100% học phí của 15 tín chỉ. | Giảng viên cơ hữu UEH được tăng thêm 20 triệu đồng thu nhập hằng tháng. | thấp | 0.1777 | Không |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả bất ngờ nhất là Cặp 5 (hai câu khác hẳn chủ đề và đối tượng: sinh viên vs giảng viên) lại có điểm tương tự (0.1777) cao hơn hẳn các cặp câu đồng nghĩa hoàn toàn như Cặp 1 (0.0871) và Cặp 2 (-0.0644).
> Điều này minh chứng rõ nét sự khác biệt giữa mô hình hàm băm giả lập (`MockEmbedder` dựa trên mã băm MD5) và mô hình biểu diễn ngữ nghĩa học sâu: MockEmbedder chỉ ánh xạ chuỗi ký tự sang vector ngẫu nhiên xác định nên không thể bảo toàn khoảng cách ngữ nghĩa. Để hệ thống RAG thực sự hiểu được văn bản, bắt buộc phải dùng các mô hình embedding ngữ nghĩa (như Sentence Transformers, OpenAI, Gemini), nơi hướng và góc giữa các vector phản ánh quan hệ khái niệm và ngữ cảnh thực tế chứ không phụ thuộc vào chuỗi ký tự bề mặt.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src` với chiến lược được phân công `sentence_2` (`SentenceChunker(max_sentences_per_chunk=2)`). **5 câu hỏi này trùng khớp với bộ câu hỏi chung của nhóm** trong [REPORT_NHOM.md](REPORT_NHOM.md). Kết quả thực tế khi chạy `python bench.py` (ghi nhận trong [ket_qua_benchmark.txt](../ket_qua_benchmark.txt)):

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Học bổng President’s Excellence của VinUni chi trả những gì? | `scholarship-renewal-policy#3`: Học bổng WIT 5%, tự động gia hạn nếu học bổng đầu vào chính duy trì... (Score: 0.2782) | 1 / 2 | Không ở Top-1 (Nhưng Gold Chunk nằm ở Top-3: `undergraduate-scholarships#4`, score: 0.2181) | "\| Học bổng WIT 5% \| Tự động gia hạn nếu học bổng đầu vào chính vẫn được duy trì. \|" |
| 2 | Sinh viên VinUni cần GPA tối thiểu bao nhiêu để duy trì học bổng 100%? | `scholarship-renewal-policy#2`: Hỗ trợ tài chính theo nhu cầu, GPA tích lũy năm xét ít nhất 2,0... (Score: 0.2214) | 1 / 2 | Có một phần (Đúng tài liệu duy trì VinUni, nhưng bị nhầm sang hàng hỗ trợ nhu cầu GPA 2,0 thay vì 100% GPA 3,2) | "\| Hỗ trợ tài chính theo nhu cầu \| GPA tích lũy của năm xét đạt ít nhất 2,0 và hoàn tất tự đánh giá E.X.C.E.L cùng cuộc trao đổi với cố vấn. \|" |
| 3 | Ở UET, học bổng loại Giỏi cho khóa QH-2023 đến QH-2025 là bao nhiêu mỗi tháng? | `scholarship-renewal-policy#3`: Học bổng WIT 5%... (Score: 0.3107) | 0 / 2 | Không (Top-1 và top-3 đều bị lệch sang tài liệu VinUni do vector giả lập) | "\| Học bổng WIT 5% \| Tự động gia hạn nếu học bổng đầu vào chính vẫn được duy trì. \|" |
| 4 | Sinh viên RMIT Việt Nam đang học cần bao nhiêu tín chỉ và GPA để xin học bổng thành tích 2026? | `undergraduate-scholarships#2`: Hỗ trợ bổ sung, Special Academic hỗ trợ thêm 5%... (Score: 0.3156) | 1 / 2 | Không ở Top-1 (Nhưng Gold Chunk nằm ở Top-3: `rmit-current-student-scholarship-2026#3`, score: 0.1968) | "Một số học bổng đặc biệt có thể cộng dồn: Special Academic hỗ trợ thêm 5% cho ngành được trường chỉ định từng năm..." |
| 5 | Ở UEH, mức hỗ trợ tài chính tối đa cho một học kỳ là bao nhiêu? | `undergraduate-scholarships#4`: Future Leader Grant nhắm đến ứng viên được học bổng 80–90%... (Score: 0.2178) | 0 / 2 | Không (Đã lọc audience=student nhưng chưa đủ lọc institution=ueh nên MockEmbedder xếp VinUni lên đầu) | "Future Leader Grant nhắm đến ứng viên được học bổng 80–90% nhưng khó chi trả 10–20% còn lại..." |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **3** / 5 (gồm Q1, Q2, Q4).
> *Ghi chú đối chiếu:* Trong điều kiện chạy giả lập `MockEmbedder`, tổng điểm đạt **3/10** (3 câu có chunk gold trong top-3). Khi đối chiếu với lần chạy TF-IDF chung của nhóm trên cùng cấu hình `sentence_2`, chiến lược này đạt **7/10** (trả về đúng Top-1 ở Q1, Q3, Q5 nhờ tần suất từ vựng đặc trưng).

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> 1. **Chiến lược lặp Header (`heading_320` của Bùi Tùng Dương):** Việc tự động đính kèm tiêu đề cấp trên vào từng chunk con đã giúp giữ ngữ cảnh phân cấp cực tốt, đưa thông tin điều kiện tín chỉ/GPA của RMIT (Q4) thẳng lên Top-1.
> 2. **Sức mạnh của Lọc Metadata kết hợp:** Thử nghiệm câu Q5 cho thấy nếu không có metadata filter (`audience=student`), tài liệu hỗ trợ giảng viên UEH sẽ chiếm vị trí Top-1 ở toàn bộ các chiến lược. Lọc metadata là lá chắn quan trọng nhất để loại bỏ hoàn toàn các tài liệu sai đối tượng trước khi xếp hạng.
> 3. **Thách thức bảo toàn bảng Markdown:** Cả nhóm cùng nhận thấy các bộ chia câu hay chia đệ quy thông thường đều có nguy cơ cắt ngang các hàng của bảng điều kiện (như bảng GPA VinUni ở Q2), đòi hỏi phải có parser nhận diện bảng chuyên dụng để bảo toàn toàn bộ hàng và tên cột.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
