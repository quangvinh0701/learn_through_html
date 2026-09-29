# Patch Notes — 17/07/2026 (index.html + hệ thống build/mã hóa)

Vá theo báo cáo `DANH-GIA-INDEX-HTML-20260717.md`. Backup nguyên trạng: `_backup-before-fix-20260717/` (build.py, make-protected.py, rebuild-all-in-one.bat, index.html, masterclass-protected.html, masterclass-all-in-one.html).

Quyết định của chủ tài liệu: giữ mật khẩu 0701 (chấp nhận mức "khóa lịch sự"), bỏ toàn bộ chặn copy, bật nén gzip.

## build.py (template shell — mục 1.4, 1.5, 2.1, 2.5)

- **Bỏ toàn bộ anti-copy trong GUARD**: xóa CSS `user-select:none`, xóa blocker copy/cut/contextmenu/selectstart/dragstart, xóa chặn Ctrl+A/C/X/S/U. Người học giờ bôi đen/copy được mọi nội dung trong bài.
- **Link ngoài mở tab mới**: GUARD giữ lại handler smooth-scroll cho anchor `#`, thêm nhánh: link `http(s)://` → tự gán `target="_blank" rel="noopener"`. Hết cảnh bấm link GitHub/docs bị nuốt mất khung bài học (trước đây 23/23 link ngoài dính lỗi này).
- **Sidebar/trang chủ gom theo group** (hàm `groupMeta()` mới): hết lặp header — trước 16 header cho 14 nhóm, giờ đúng 14. File 23 (dbt) nằm trong khối "Data Modeling" cùng 06/07; file 24 (MLOps) nằm trong "GenAI & AI Engineering" cùng 22. Thứ tự prev/next (Alt+←/→) vẫn theo số 01→24.
- **Số đếm tĩnh "15" → placeholder `__COUNT__`**: build.py bơm số thật (24) lúc build; hết vết tích bản 15 file cũ ở docCount/pmTotal/tbTotal.

## make-protected.py (trang khóa — mục 1.2, 1.3, 2.3, 2.7)

- **Nén gzip level 9 trước khi mã hóa** (payload thêm cờ `"gz":1`); phía browser giải nén bằng `DecompressionStream('gzip')` (cần trình duyệt ~2023+; có kiểm tra và báo lỗi rõ nếu thiếu). Kết quả: **index.html 9,97MB → 2,94MB** (−70%).
- **Chip trên trang khóa đếm động**: parse `meta-data` từ file nguồn → hiển thị "24 masterclass" (trước hardcode sai "20 modules"); fallback "Data Engineering" nếu mã hóa file không phải bản gộp.
- **Phân biệt lỗi**: pre-check `crypto.subtle` (thiếu → báo "mở qua file:// hoặc HTTPS/localhost", không còn báo nhầm sai mật khẩu khi host HTTP thường); catch chỉ báo "Sai mật khẩu" với `OperationError`, lỗi khác hiện tên lỗi.
- **getpass**: chạy không tham số sẽ hỏi mật khẩu ẩn thay vì bắt buộc truyền qua argv.

## rebuild-all-in-one.bat (mục 1.6)

- Sau build.py giờ **tự hỏi mật khẩu và mã hóa lại cả index.html + masterclass-protected.html** — chặn tái diễn lỗi "bản mã hóa lỗi thời" (đã xảy ra 10/07 và một lần nữa phát hiện hôm nay, xem dưới). Enter bỏ trống = bỏ qua mã hóa, có cảnh báo lỗi thời.
- Xóa ghi chú cũ "kiểm tra module 19 MLOps".

## Lỗi tiềm ẩn phát hiện thêm khi verify

Bản gộp cũ (build 16/07 15:35) chứa **bản cũ của 5 file nguồn**: 05/11/13 thiếu khối JS nút copy-code mới thêm, 12 thiếu JS điều hướng tab, 15 thừa 34 byte NUL rác ở cuối. Bản build hôm nay đọc lại nguồn hiện tại → đã tự đồng bộ; verify 24/24 file trong bundle khớp byte-identical với file nguồn trên đĩa.

## Verify đã chạy

- Giải mã round-trip index.html và masterclass-protected.html bằng 0701 + gunzip → MD5 khớp masterclass-all-in-one.html mới.
- Sai mật khẩu → `InvalidTag`/`OperationError` (đúng nhánh báo "Sai mật khẩu").
- `node --check` pass cho script shell, script trang khóa, script GUARD; `py_compile` pass cho build.py + make-protected.py.
- Mô phỏng render: 14 group header, không trùng; docCount/pmTotal/tbTotal = 24; chip = "24 masterclass".

## Còn để ngỏ (chưa làm, theo thứ tự đáng làm)

- 2 bản mã hóa trùng vai trò (index.html = masterclass-protected.html) — cân nhắc bỏ một.
- Trang khóa còn phụ thuộc Google Fonts + ảnh Unsplash hotlink.
- Nhóm "Lakehouse" (16) vs "Warehouse & Lakehouse" (20) tên gần trùng — quyết định nội dung, không đụng.

---

# Đợt 2 cùng ngày — Đại tu giao diện học (learning UX)

Toàn bộ nằm trong template shell của `build.py` — KHÔNG sửa 24 file nguồn, mọi thứ inject lúc runtime qua `contentDocument`. Quyết định của chủ tài liệu: không dark mode, có panel ghi chú.

## Vấn đề UX phát hiện khi khảo sát

- Tab module (10–23 tab/bài) không lưu trạng thái — đóng/mở lại là về module 1, mất vị trí cuộn.
- Nút copy CHẾT ở 5 file (12/14/15/19/20: có markup `.term-copy` nhưng thiếu JS `attachCopy`); ~200 khối terminal không có nút (file 19: 72 khối chỉ 2 nút); toàn bộ `<pre>` không có nút copy.
- Phím tắt tê liệt khi focus trong iframe; tìm kiếm chỉ nhảy tới kết quả đầu; không có thước đo độ dài bài/tiến độ module.

## Tính năng mới (shell v2)

1. **Resume chính xác**: lưu module đang mở + vị trí cuộn từng bài (`mc_aio_pos`), mở lại đúng chỗ; nút "▶ Tiếp tục học" trên trang chủ kèm tên bài + module.
2. **Copy code toàn diện**: kích hoạt mọi nút `.term-copy` chưa bound (tôn trọng `dataset.bound` nên không double-bind với file có JS sẵn); tự thêm nút vào `.term-bar` thiếu; thêm nút nổi cho `<pre>` ≥ 25 ký tự; fallback `execCommand` khi Clipboard API bị chặn.
3. **Phím tắt xuyên iframe**: Alt+←/→ chuyển bài, **Alt+↑/↓ chuyển module (mới)**, `/` tìm kiếm, Ctrl+B ẩn sidebar — hoạt động cả khi focus trong bài (listener gắn thẳng vào doc của iframe).
4. **Bộ đếm module**: topbar hiện "M x/y ▾" bấm ra dropdown danh sách module (đánh dấu ✓ đã xem, bấm để nhảy); sidebar mỗi bài hiện "đã xem x/y · thời lượng"; xem đủ → chuyển xanh.
5. **Thanh tiến độ đọc** 3px dưới topbar theo % cuộn.
6. **Thời lượng đọc ước tính** (build.py đếm từ, 220 từ/phút): card trang chủ + sidebar; hero hiện tổng ≈ 39 giờ.
7. **Điều hướng kết quả tìm kiếm**: topbar hiện "‹ n/tổng ›" khi mở bài từ tìm kiếm, tự kích hoạt đúng module chứa kết quả.
8. **Cỡ chữ A−/A+** (zoom 80–140%, lưu `mc_aio_zoom`).
9. **Ghi chú theo bài** (`mc_aio_notes`) — bản v2 chỉn chu (làm lại theo góp ý):
   - 2 tab: **"Bài này"** (soạn thảo) / **"Tất cả (n)"** (danh sách mọi bài có ghi chú, preview 2 dòng + thời gian sửa, bấm để nhảy tới bài đó);
   - Trạng thái lưu hiện rõ: "Đang lưu…" → "Đã lưu ✓" (xanh) → "Sửa: x phút trước"; đếm ký tự;
   - Nút **"+ mốc module"** chèn tiêu đề `## M12 · <tên module đang mở>` vào ghi chú;
   - Nút xoá (có confirm), xuất `.md` kèm ngày xuất + thời gian sửa từng bài;
   - Sidebar hiện icon ✎ cam ở bài có ghi chú; badge đếm tổng số bài có ghi chú;
   - Phím tắt **Alt+N** mở/đóng; Escape đóng panel trước khi về Trang chủ; animation trượt mượt;
   - Dữ liệu format cũ (chuỗi thuần) tự migrate sang `{t, u}` (nội dung + timestamp), không mất gì.
10. "Reset tiến độ" giờ xoá cả module đã xem + vị trí đọc nhưng GIỮ ghi chú.

## Verify

- `node --check` pass (script shell mới ~500 dòng, script gate, GUARD).
- Smoke test jsdom: 24 item / 14 nhóm, thời lượng render đúng, tìm "shuffle" ra 576 kết quả/6 file, badge đúng.
- Round-trip mã hóa 0701 + gunzip khớp MD5 cả 2 bản; index.html ~2,9MB.
- **Giới hạn**: sandbox không có browser thật (tải Chromium bị chặn) — hành vi trong iframe (resume, copy, dropdown module) đã rà logic thủ công theo pattern `highlightViewer` cũ, nhưng nên mở thử trên máy để xác nhận. Checklist thử nhanh: mở 1 bài → chuyển sang module giữa → cuộn → F5 → phải quay đúng chỗ; bấm copy ở file 12; Alt+↓ khi đang bấm trong nội dung; gõ ghi chú rồi xuất .md.
