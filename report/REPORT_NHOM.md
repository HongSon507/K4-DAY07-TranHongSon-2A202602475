# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** G15
**Thành viên:** Đinh Đức Thái, Trần Hồng Sơn, Hoàng Trung Hiếu, Bùi Tùng Dương, Đàm Quang Sơn
**Ngày:** 19/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Học bổng và hỗ trợ tài chính trong đại học, đối chiếu VinUni, UEH, UET và RMIT Việt Nam.

**Tại sao nhóm chọn chủ đề này?**
Bảy văn bản được chọn từ các bản nháp trong `data/` vì có nguồn chính thức, con số hoặc điều kiện kiểm chứng được, và ít trùng lặp. Bộ cuối gồm sáu tài liệu dành cho sinh viên và một tài liệu hỗ trợ giảng viên để kiểm thử lọc `audience`; trường `institution` ngăn trộn chính sách giữa các trường. Nội dung được biên tập ngắn bằng tiếng Việt, giữ điều kiện, mức hỗ trợ, mốc thời gian và bảng cần thiết.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Học bổng đầu vào cử nhân VinUni | [VinUni Admissions](https://admissions.vinuni.edu.vn/scholarship-and-financial-aid/undergraduate-programs/scholarships/) | 2026-09-19 / not-stated | 1.481 | `student`, `vinuni`, `merit-scholarship` |
| 2 | Duy trì học bổng đầu vào VinUni | [VinUni Policy](https://policy.vinuni.edu.vn/all-policies/criteria-to-maintain-the-entry-scholarship-and-financial-aid-support/) | 2026-09-19 / GDL-SAM-004-V2.1 | 1.399 | `student`, `vinuni`, `renewal-policy` |
| 3 | Học bổng hỗ trợ học tập UEH | [UEH DSA](https://dsa.ueh.edu.vn/chuyen-trang-chinh-sach-ho-tro-tai-chinh/hoc-bong/) | 2026-09-19 / not-stated | 836 | `student`, `ueh`, `need-based-scholarship` |
| 4 | Hỗ trợ tài chính giảng viên UEH | [UEH](https://ueh.edu.vn/college/cob/vi/ueh-ban-hanh-chinh-sach-dai-ngo-dot-pha-chieu-mo-giu-chan-nhan-tai-kien-tao-vi-the-quoc-te-76541) | 2026-09-19 / not-stated | 843 | `faculty`, `ueh`, `faculty-funding` |
| 5 | Học bổng khuyến khích UET 2025–2026 | [UET](https://uet.edu.vn/cap-hoc-bong-khuyen-khich-hoc-tap-trong-hoc-ky-i-nam-hoc-2025-2026-cho-sinh-vien/) | 2026-09-19 / 2339/QĐ-ĐHCN | 1.110 | `student`, `uet`, `merit-scholarship` |
| 6 | Học bổng Cử nhân Kinh doanh RMIT 2026 | [RMIT](https://www.rmit.edu.vn/study-at-rmit/scholarships/future-undergraduate-student-scholarships/bachelor-of-business-scholarship) | 2026-09-19 / 2026 | 1.004 | `student`, `rmit-vietnam`, `merit-scholarship` |
| 7 | Học bổng thành tích RMIT 2026 | [RMIT](https://www.rmit.edu.vn/study-at-rmit/scholarships/current-student-scholarships) | 2026-09-19 / 2026 | 957 | `student`, `rmit-vietnam`, `current-student-scholarship` |

Số ký tự tính trên phần nội dung sau front matter. Toàn bộ dữ liệu nộp bài nằm trong [`data/hoc-bong-chon-loc/`](../data/hoc-bong-chon-loc/), cùng [`sources.csv`](../data/hoc-bong-chon-loc/sources.csv) và [`urls.csv`](../data/hoc-bong-chon-loc/urls.csv). Với nguồn không nêu phiên bản, ghi `not-stated` thay vì suy đoán.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu gồm bản tóm lược từ các trang công khai của bốn trường, không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc `not-stated`) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `scholarship-renewal-policy` | Mã ổn định để đối chiếu file và xóa mọi chunk cùng nguồn. |
| `title` | string | `Tiêu chí duy trì học bổng đầu vào` | Hiển thị tên nguồn cho người đánh giá. |
| `source_url` | HTTPS URL | `https://policy.vinuni.edu.vn/...` | Truy vết và kiểm tra lại điều khoản gốc. |
| `retrieved_at` | ngày ISO | `2026-09-19` | Biết thời điểm dữ liệu được thu thập. |
| `document_version` | string | `GDL-SAM-004-V2.1` | Ưu tiên phiên bản chính sách có số hiệu; `not-stated` nếu nguồn không nêu. |
| `audience` | enum | `student`, `faculty` | Lọc đúng đối tượng trước khi xếp hạng. |
| `institution` | string | `vinuni`, `ueh`, `uet`, `rmit-vietnam` | Không trộn điều kiện của các trường khác nhau. |
| `department` | string | `admissions`, `student-affairs` | Thu hẹp theo đơn vị phụ trách. |
| `category` | string | `renewal-policy`, `faculty-funding` | Phân biệt điều kiện duy trì, tuyển sinh và hỗ trợ giảng viên. |
| `language` | string | `vi` | Chọn tài liệu theo ngôn ngữ phần nội dung đã biên tập. |

**Nghiệm thu Checkpoint 2:** `python scripts/check_corpus.py` → `OK: 7 Markdown files; urls.csv and sources.csv match; audiences: faculty, student`.

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

Năm cấu hình dưới đây được chạy lại bằng cùng bộ 7 văn bản, cùng 5 câu hỏi và cùng một bộ mã hóa TF-IDF trong [`bench.py`](../bench.py). Đây là **phép so sánh chuẩn hóa của nhóm**. Sau khi đối chiếu đủ 5 báo cáo cá nhân của các thành viên trong nhóm, chỉ báo cáo của Đàm Quang Sơn khớp cả cấu hình, bộ câu hỏi và backend với một hàng của bảng này; các báo cáo còn lại khác ít nhất một yếu tố. Vì vậy không dùng điểm cá nhân để xếp hạng năm cấu hình chuẩn hóa.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare(body, chunk_size=200)` trên nội dung sau front matter của ba tài liệu. Độ dài là số ký tự trung bình mỗi chunk; nhận xét ngữ cảnh dựa trên việc quan sát vị trí điều kiện và bảng Markdown.

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| VinUni học bổng đầu vào | FixedSizeChunker (`fixed_size`) | 8 | 185,1 | Có thể cắt giữa tên học bổng và mức hỗ trợ. |
| VinUni học bổng đầu vào | SentenceChunker (`by_sentences`) | 4 | 368,5 | Giữ câu giải thích trọn vẹn; chunk dài hơn. |
| VinUni học bổng đầu vào | RecursiveChunker (`recursive`) | 11 | 133,2 | Dễ truy xuất chi tiết; một số chunk thiếu tên mục. |
| VinUni duy trì học bổng | FixedSizeChunker (`fixed_size`) | 7 | 199,9 | Có thể cắt ngang một hàng điều kiện GPA. |
| VinUni duy trì học bổng | SentenceChunker (`by_sentences`) | 4 | 348,8 | Giữ câu ngoài bảng; bảng vẫn có thể bị chia. |
| VinUni duy trì học bổng | RecursiveChunker (`recursive`) | 9 | 154,3 | Tách nhỏ bảng; cần giữ tiêu đề cột khi truy xuất. |
| UET mức học bổng | FixedSizeChunker (`fixed_size`) | 6 | 185,0 | Có nguy cơ mất nhãn `Giỏi` của cột. |
| UET mức học bổng | SentenceChunker (`by_sentences`) | 3 | 369,0 | Ít chunk, nhiều hàng cùng xuất hiện. |
| UET mức học bổng | RecursiveChunker (`recursive`) | 7 | 157,4 | Chỉ hữu ích khi chunk giữ hàng và nhãn cột. |

### Năm cấu hình trong benchmark chung

| Cấu hình | Cách chia và lý do thử |
|---|---|
| `fixed_220` | Cắt 220 ký tự, chồng lấn 30 ký tự để có đường cơ sở đơn giản và giảm mất thông tin ở ranh giới. |
| `sentence_2` | Ghép tối đa hai câu; kỳ vọng giữ nguyên phát biểu về điều kiện và mức học bổng. |
| `recursive_280` | Chia theo ranh giới văn bản đến tối đa 280 ký tự; giảm độ dài chunk và tăng độ chính xác vị trí. |
| `heading_320` | Cắt theo tiêu đề Markdown; khi mục dài, lặp lại tiêu đề trên các phần con để giữ ngữ cảnh. |
| `paragraph_360` | Gom các đoạn Markdown liền kề tới 360 ký tự; giữ đoạn và hàng bảng khi vừa giới hạn. |

Hai chiến lược tùy chỉnh nằm trong `bench.py` (`HeadingChunker`, `ParagraphChunker`). Ý chính của chiến lược theo tiêu đề:

```python
sections = re.split(r"(?=^#{1,3} )", text, flags=re.MULTILINE)
for part in RecursiveChunker(chunk_size=body_size).chunk(body):
    chunks.append(f"{heading}\n{part}")
```

Chiến lược theo đoạn tách tại dòng trắng, gom đoạn đến giới hạn rồi dùng `RecursiveChunker` cho đoạn quá dài. Cả hai là cấu hình thử nghiệm, chưa có cơ chế chuyên dụng để bảo toàn cả một bảng Markdown.

### Đối chiếu với năm báo cáo cá nhân

| Thành viên và file | Chiến lược/backend được ghi trong báo cáo | Kết quả được ghi | Khả năng đối chiếu với benchmark chung |
|---|---|---|---|
| Đinh Đức Thái (báo cáo cá nhân) | Ghi dùng `MockEmbedder`; mục 5 không ghi rõ tham số chunker và dùng 5 câu hỏi khác bộ chung. | 3/5 lượt có `doc_id` liên quan; tự chấm 9/10. | Không đủ căn cứ chuyển 3/5 lượt trúng tài liệu thành 9/10 theo nội dung chunk và câu trả lời. |
| [Trần Hồng Sơn](REPORT_CANHAN.md) | `sentence_2`, bảng cá nhân ghi kết quả `MockEmbedder`. | Mô tả 3/10 (3/5 câu có bằng chứng top-3 trên Mock); hoàn thành code 42/42 tests pass (60/60). | Cùng câu hỏi với bộ chung, khác backend; cấu hình `sentence_2` trong benchmark TF-IDF đạt 7/10. |
| Hoàng Trung Hiếu (báo cáo cá nhân) | `FixedSizeChunker(500, 50)` với `LocalEmbedder`; báo cáo tự ghi bốn câu còn là bản nháp. | Tự chấm 3/10 trên 5 câu nháp. | Khác cấu hình, backend và câu hỏi; chưa có lần chạy cá nhân trên bộ 5 câu chính thức. |
| Bùi Tùng Dương (báo cáo cá nhân) | `FixedSizeChunker(500, 50)` với TF-IDF, 20 chunk; Q2–Q4 khác câu hỏi chính thức. | 4/5 câu có bằng chứng theo nội dung, **8/10 theo vị trí bằng chứng**; chưa chấm câu trả lời của agent. | Không thể coi 8/10 này là điểm theo rubric chung; báo cáo cá nhân chưa chứng minh đã chạy `heading_320`. |
| Đàm Quang Sơn (báo cáo cá nhân) | `paragraph_360` với TF-IDF và bộ 5 câu chung. | 5/5 câu có bằng chứng top-3, 6/10 theo rubric vì agent sai Q2 và Q5. | Khớp log của cấu hình `paragraph_360` trong benchmark chung. |

Các số trong cột kết quả là **số do từng báo cáo tự ghi**, chưa phải một bảng điểm cá nhân đồng nhất. Trong năm báo cáo, chưa có báo cáo cá nhân nào ghi đã chạy `heading_320` hoặc `recursive_280` trên bộ câu hỏi chính thức; hai cấu hình này có log ở benchmark nhóm. Cần để người phụ trách xác nhận hoặc chạy lại trước khi ghi tên họ là tác giả kết quả đó.

### So sánh năm cấu hình trên cùng điều kiện

| Cấu hình | Số chunk / độ dài TB | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| `fixed_220` | 43 / 202,6 | 7 | Q1, Q3, Q5 đúng ở top-1. | Cắt ngang hàng bảng GPA ở Q2. |
| `sentence_2` | 32 / 237,2 | 7 | Ít chunk hơn, Q1, Q3, Q5 đúng ở top-1. | Q2 không tìm được hàng GPA. |
| `recursive_280` | 40 / 189,4 | 7 | Q1, Q3, Q5 đúng ở top-1. | Q2 vỡ ngữ cảnh bảng. |
| `heading_320` | 41 / 219,6 | 7 | Q4 lên top-1 nhờ lặp tiêu đề RMIT. | Q5 chỉ ở top-2; Q2 vẫn lỗi. |
| `paragraph_360` | 32 / 237,0 | 6 | Q2 có hàng GPA ở top-3. | Q3/Q4 chỉ ở top-2/3; bộ trả lời chọn sai dòng ở Q5. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
Trong lần chạy này, bốn cấu hình cùng đạt 7/10; chọn `sentence_2` làm cấu hình trình diễn vì tạo 32 chunk, ít hơn các cấu hình 7 điểm còn lại, và trả lời đúng Q1, Q3, Q5 với bằng chứng ở top-1. Với câu hỏi RMIT Q4, `heading_320` tốt hơn do đưa cả hai ngưỡng vào top-1. Cả năm chưa xử lý tốt bảng GPA VinUni, nên kết luận chỉ áp dụng cho bộ 5 câu hỏi và bộ mã hóa hiện tại.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Bộ câu hỏi chính thức dùng trong benchmark nhóm

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi cố định trong `bench.py`; bảng đối chiếu ở Mục 2 cho thấy một số báo cáo cá nhân chưa chạy đúng bộ này.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Học bổng President’s Excellence của VinUni chi trả những gì? | Toàn bộ học phí và chi phí sinh hoạt. | `undergraduate-scholarships`, câu về President’s Excellence. |
| 2 | Sinh viên VinUni cần GPA tối thiểu bao nhiêu để duy trì học bổng 100%? | GPA tích lũy của năm xét ít nhất **3,2**; còn có điều kiện kỷ luật, E.X.C.E.L và trao đổi với cố vấn. | `scholarship-renewal-policy`, hàng `Học bổng toàn phần hoặc 100%`. |
| 3 | Ở UET, học bổng loại Giỏi cho khóa QH-2023 đến QH-2025 là bao nhiêu mỗi tháng? | **3.500.000đ/tháng** ở hàng `Chuẩn QH-2023 đến QH-2025`, cột `Giỏi`. | `uet-merit-scholarship-2025-2026`, bảng định mức. |
| 4 | Sinh viên RMIT Việt Nam đang học cần bao nhiêu tín chỉ và GPA để xin học bổng thành tích 2026? | Ít nhất **96 tín chỉ** tại RMIT Việt Nam và GPA tích lũy **3,4/4,0**. | `rmit-current-student-scholarship-2026`, đoạn điều kiện xét. |
| 5 | Ở UEH, mức hỗ trợ tài chính tối đa cho một học kỳ là bao nhiêu? | Học bổng toàn phần cho sinh viên bằng **100% học phí trung bình của 15 tín chỉ**. | `ueh-learning-support-scholarship`, mục `Mức học bổng`; giới hạn UEH rồi gọi `metadata_filter={"audience": "student"}`. |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | President’s Excellence | Cả năm cấu hình | Có, top-1 | Agent trích đúng học phí và sinh hoạt. |
| 2 | GPA duy trì 100% | `paragraph_360` | Có, top-3 | Chỉ cấu hình này đưa hàng `3,2` vào top-3; agent vẫn chọn sai hàng. Các cấu hình khác: 0 điểm. |
| 3 | UET loại Giỏi | Bốn cấu hình 7 điểm (đồng hạng) | Có, top-1 | Dòng trả lời gồm đủ hàng bảng, nhưng cần đọc theo thứ tự cột `Xuất sắc / Giỏi / Khá`. |
| 4 | RMIT tín chỉ và GPA | `heading_320` | Có, top-1 | Lặp tiêu đề giúp chunk chứa cả `96 tín chỉ` và `3,4/4,0` lên đầu. |
| 5 | UEH mức toàn phần | `fixed_220`, `sentence_2`, `recursive_280` | Có, top-1 sau lọc | Bỏ `audience` thì tài liệu UEH dành cho giảng viên đứng top-1 ở cả năm cấu hình. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
Ở Q5, cả hai nhánh A/B cùng dùng các chunk có `institution=ueh` từ bộ 7 tài liệu. Nhánh thử gọi `search_with_filter(..., metadata_filter={"audience": "student"})`; khi chưa lọc `audience`, chunk giảng viên UEH đứng top-1 ở cả năm cấu hình. Ba cấu hình đạt 2 điểm ở Q5; `heading_320` đưa bằng chứng lên top-2, còn `paragraph_360` có bằng chứng top-1 nhưng bộ trả lời chọn dòng khác. Điều này cho thấy lọc đúng tài liệu chưa bảo đảm câu trả lời cuối đúng.

**Cách chạy và giới hạn phép đo:** `python bench.py` tạo [`ket_qua_benchmark.txt`](../ket_qua_benchmark.txt). Script dùng TF-IDF từ thư viện chuẩn, một từ vựng cố định dựng trên 7 văn bản, `EmbeddingStore` và `KnowledgeBaseAgent` với bộ trả lời trích một dòng; không dùng API embedding hoặc LLM. Chấm 2 khi chunk đúng đứng top-1 và câu trả lời chứa đủ dấu mốc, 1 khi chunk đúng ở top-3 nhưng trả lời thiếu hoặc không đứng đầu, 0 khi không có chunk đúng trong top-3. Dấu mốc là phép kiểm tự động, không thay thế việc đọc câu trả lời: Q3 trả về cả hàng bảng, người đọc phải xác định cột `Giỏi`; ID chunk có thể thay đổi khi sửa bộ chia hoặc văn bản. Điểm trong bảng là kết quả một lần chạy trên bộ dữ liệu cố định, không phải kết quả của dịch vụ embedding ngữ nghĩa.

**Điểm cần phân biệt khi đọc báo cáo cá nhân:** Điểm cosine của `MockEmbedder`, TF-IDF và `LocalEmbedder` không cùng thang đánh giá thực nghiệm nên không xếp hạng trực tiếp. Báo cáo của Bùi Tùng Dương ghi 8/10 theo vị trí bằng chứng mà chưa gọi agent, trong khi 7/10 ở bảng nhóm tính cả dấu mốc trong câu trả lời trích xuất. Báo cáo của Trần Hồng Sơn ghi kết quả mock 3/10 nhưng bảng tự đánh giá 10/10; cần đối chiếu lại trước khi dùng làm điểm cá nhân chính thức.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

- Demo `python scripts/check_corpus.py`, sau đó `python bench.py`; mở Q5 trong log để thấy tài liệu giảng viên top-1 khi chỉ lọc `ueh` và tài liệu sinh viên khi thêm `audience=student`.
- Mở Q2 trong văn bản nguồn và log: hàng GPA **3,2** có trong dữ liệu nhưng bốn chiến lược không truy xuất được chunk chứa hàng đó ở top-3; cấu hình theo đoạn tìm được ở top-3 nhưng bộ trả lời vẫn chọn sai.
- Đối chiếu Q4: lặp tiêu đề trong `heading_320` đưa điều kiện RMIT lên top-1, các cách chia khác đưa lên top-2 hoặc top-3.
- Đọc bảng đối chiếu năm báo cáo cá nhân: cùng chủ đề nhưng khác câu hỏi, backend và cách chấm có thể cho những con số không so sánh được. Báo cáo của Hoàng Trung Hiếu tự ghi điểm cosine 0,7338 cho hai câu GPA **3,2** và **2,0** bằng mô hình đa ngữ; điều này gợi ý phải kiểm giá trị số trong chunk, dù hai câu gần nhau về mặt biểu đạt.

**Bài học rút ra khi so sánh trong nhóm:**
Cùng 7 tài liệu, vị trí bằng chứng thay đổi vì các bộ chia giữ tiêu đề, câu và hàng bảng theo cách khác nhau. Chia nhỏ giúp tìm một điều kiện ngắn, nhưng có thể cắt mất tên cột hoặc tên chương trình; vì vậy phải xem chính chunk và câu trả lời, không chỉ nhìn `doc_id` hay điểm cosine. Báo cáo của Bùi Tùng Dương ghi 5/5 nếu chỉ tính `doc_id` nhưng 4/5 nếu đòi chunk chứa bằng chứng; đây là minh họa thêm, trên bộ câu hỏi khác bộ chính thức. Metadata `institution` và `audience` giải quyết nhầm đối tượng ở Q5 trước khi xếp hạng.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
Tạo bộ chia riêng cho bảng Markdown: lặp tiêu đề cột và giữ nguyên từng hàng cùng tên học bổng để Q2 không mất quan hệ `100% → 3,2`. Ghi thêm mã hàng/mục và ngày hiệu lực vào metadata, rồi đánh giá bằng tập câu hỏi lớn hơn và một bộ trả lời có thể kiểm tra được liên kết giữa cột và giá trị. Cần đối chiếu lại các bản tóm lược với trang nguồn trước khi dùng cho tư vấn học bổng thực tế.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 9 / 10 |
| Thiết kế chiến lược (Strategy Design) | 11 / 15 — có năm cấu hình chuẩn hóa, thiếu xác nhận chạy riêng của từng người |
| Chất lượng truy xuất (Retrieval Quality) | 7 / 10 |
| Thuyết trình (Demo) | 0 / 5 — chưa có bằng chứng đã trình bày trực tiếp |
| **Tổng phần nhóm, tạm tính trước khi thuyết trình** | **27 / 40** |

Điểm tự đánh giá dựa trên corpus và benchmark có thể tái chạy; điểm thuyết trình sẽ cập nhật sau buổi demo. Điểm chất lượng lấy cấu hình tốt nhất, không cộng điểm của nhiều cấu hình. Việc thống nhất lại năm báo cáo cá nhân với bộ câu hỏi chính thức và xác nhận ai chạy `heading_320`/`recursive_280` là phần nhóm còn phải hoàn tất trước khi nộp.
