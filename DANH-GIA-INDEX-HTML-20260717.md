# Đánh giá file index.html (bản mã hóa mật khẩu) — 17/07/2026

Phạm vi: lớp vỏ bảo vệ (password gate) + shell trình đọc all-in-one mà nó giải mã ra. Không tái kiểm định chất lượng nội dung 24 bài học (đã có `DANH-GIA-BO-TAI-LIEU-DE.md`). Phương pháp: giải mã thật bằng mật khẩu 0701, đối chiếu MD5 với bản gốc, đọc toàn bộ code của gate (`make-protected.py`) và shell (`build.py` template), mô phỏng logic render, đo tốc độ brute-force thực tế.

## 0. Xác nhận trước khi chê

- Giải mã thành công bằng 0701. Nội dung bên trong **khớp 100%** (MD5 `dc55496f...`) với `masterclass-all-in-one.html` bản mới nhất (16/07, đủ 24 file kể cả 23-dbt và 24-MLOps). Cảnh báo "bản mã hóa là bản gộp CŨ" trong PATCH-NOTES **đã được khắc phục**.
- `masterclass-protected.html` cũng giải mã ra đúng nội dung đó → hai file là bản sao vai trò của nhau.
- Phần crypto triển khai **đúng chuẩn**: AES-256-GCM (authenticated encryption — sửa 1 byte ciphertext là giải mã fail), PBKDF2-SHA256 600.000 vòng, salt 16B + IV 12B sinh ngẫu nhiên mỗi lần build. Không có lỗi triển khai mã hóa.

## 1. Sai sót (bug) — xếp theo mức nghiêm trọng

### 1.1. Mật khẩu 4 chữ số vô hiệu hóa toàn bộ lớp mã hóa — NGHIÊM TRỌNG (nếu mục tiêu là chống lộ tài liệu)

Không gian mật khẩu chỉ 10.000 PIN, mà file mã hóa nằm trọn trong tay người nhận → brute-force offline (thử mật khẩu ngoại tuyến), không có gì ngăn được. Đo thật trên sandbox: 1 lần thử PBKDF2-600k mất 0,41 giây/1 core Python → quét hết 10.000 PIN mất **~68 phút 1 core, ~9 phút với 8 core**; dùng hashcat trên GPU thì tính bằng giây tới vài phút. 600k iterations chỉ có ý nghĩa khi mật khẩu là passphrase dài (≥ 4-5 từ ngẫu nhiên). Với PIN 4 số, đây thực chất là "khóa lịch sự" chống người tò mò, không chống được ai chủ đích.

**Fix:** nếu cần bảo mật thật → đổi sang passphrase dài. Nếu chỉ cần khóa lịch sự → giữ nguyên nhưng biết rõ giới hạn.

### 1.2. Chip "20 modules" trên trang khóa — SAI SỐ LIỆU

Trang nhập mật khẩu hiển thị chip "20 modules" trong khi bộ hiện có 24 masterclass. Nguyên nhân: hardcode trong `TEMPLATE` của `make-protected.py` (khối `.chips`). Người nhận nhìn thấy con số sai ngay ở cửa.

**Fix:** sửa thành "24 masterclass", hoặc để make-protected.py nhận số lượng làm tham số.

### 1.3. Mọi lỗi đều báo "Sai mật khẩu" — CHẨN ĐOÁN SAI MÔI TRƯỜNG

Khối `catch(e)` trong hàm `unlock()` gộp tất cả exception. Hệ quả cụ thể: `crypto.subtle` (WebCrypto) chỉ tồn tại trong secure context (HTTPS, localhost, file://). Nếu host file qua HTTP thường (vd chia sẻ qua LAN `http://192.168.x.x`), `crypto.subtle` là `undefined` → TypeError → người dùng nhập **đúng** mật khẩu vẫn bị báo "Sai mật khẩu. Vui lòng thử lại." — không thể tự chẩn đoán.

**Fix:** kiểm tra `if(!window.crypto || !crypto.subtle)` ngay đầu, báo riêng "Cần mở qua HTTPS/localhost hoặc mở file trực tiếp"; chỉ báo sai mật khẩu với `OperationError`.

### 1.4. 23/23 link ngoài trong bài học nuốt mất khung đọc

Toàn bộ link external (`https://github.com/...`, `airflow.apache.org`, OWASP... trong các bài 06, 08, 12) **không có `target="_blank"`**. Trong iframe `srcdoc`, bấm link → chính iframe điều hướng sang trang ngoài, mất bài đang đọc, phải bấm lại menu. Script GUARD đã intercept link `#` nội bộ nhưng bỏ qua link ngoài.

**Fix rẻ nhất:** trong chuỗi `GUARD` (build.py), chèn thêm `<base target="_blank">`, hoặc thêm nhánh xử lý trong click handler sẵn có: link không phải `#` → `a.target='_blank'`.

### 1.5. Sidebar và trang chủ lặp tiêu đề nhóm

`buildNav()`/`buildHome()` tạo header nhóm mỗi khi `group` đổi theo thứ tự số thứ tự file. Vì file 23 (Data Modeling) và 24 (GenAI) nằm cuối, kết quả render thực tế là **16 header cho 14 nhóm**: "Data Modeling" xuất hiện 2 lần (chỗ 06-07 và chỗ 23), "GenAI & AI Engineering" 2 lần (22 và 24). Cuối sidebar là 3 nhóm liên tiếp mỗi nhóm 1 bài, trùng tên với nhóm phía trên — nhìn như lỗi.

**Fix:** một trong hai — (a) sửa buildNav/buildHome gom item theo group trước khi render (giữ thứ tự xuất hiện đầu tiên của group); (b) đơn giản hơn: đổi group của 23/24 trong `00-index.html` thành nhóm riêng, vd "Phụ lục 2025+".

Liên quan taxonomy: nhóm "Lakehouse" (bài 16) và "Warehouse & Lakehouse" (bài 20) là 2 nhóm tên gần trùng — nên hợp nhất hoặc đổi tên một nhóm.

### 1.6. Quy trình build không tự đồng bộ bản mã hóa — LỖI QUY TRÌNH ĐÃ TỪNG XẢY RA

`rebuild-all-in-one.bat` chỉ chạy `build.py`, không chạy tiếp `make-protected.py` → sau mỗi lần sửa nội dung, `index.html` và `masterclass-protected.html` lập tức lỗi thời cho tới khi nhớ chạy tay. Chính PATCH-NOTES 10/07 đã ghi nhận sự cố này một lần. Hiện tại đã đồng bộ (16/07) nhưng cơ chế gây lỗi vẫn còn nguyên. Phụ: comment trong .bat vẫn nói "kiểm tra module 19 MLOps" — đã lỗi thời (MLOps giờ là 24).

**Fix:** thêm vào .bat sau build.py:
```bat
set /p PW=Nhap mat khau:
python make-protected.py "%PW%" masterclass-all-in-one.html index.html
python make-protected.py "%PW%" masterclass-all-in-one.html masterclass-protected.html
```

## 2. Thiếu sót / trade-off cần biết rõ

### 2.1. Anti-copy chỉ mang tính răn đe, và có tác dụng phụ lên người học

GUARD chặn select/copy/cut/context-menu/Ctrl+A-C-X-S-U **bên trong iframe**. Nhưng: F12/DevTools không (và không thể) bị chặn; sau khi mở khóa, toàn bộ base64 của 24 bài nằm ngay trong DOM — 1 dòng console decode được tất cả; Ctrl+S ở document ngoài không bị chặn. Tức là chống copy chỉ cản người dùng phổ thông.

Tác dụng phụ đáng cân nhắc hơn: **học viên không bôi đen/copy được code trong một bộ tài liệu dạy code** — muốn chạy thử phải gõ lại tay từng lệnh. Với định hướng "đọc hiểu cơ chế" thì chấp nhận được, nhưng nếu muốn người học chạy lab thì nên nới: cho phép select/copy riêng trong `<pre>/<code>` (thêm exception vào CSS user-select và handler copy của GUARD).

### 2.2. Phím tắt chết khi focus nằm trong bài học

Listener `keydown` (Alt+←/→ chuyển bài, `/` tìm kiếm, Ctrl+B ẩn sidebar) chỉ gắn ở document ngoài. Ngay khi người dùng click vào nội dung (focus vào iframe), toàn bộ phím tắt mất tác dụng cho tới khi click ra sidebar/topbar. Fix: GUARD trong iframe forward các tổ hợp này lên parent qua `parent.postMessage`.

### 2.3. Kích thước phình ×1,78 và chi phí mở trang

Chuỗi encode hiện tại: nội dung gốc (~5,6MB) → base64 trong shell (+33% → 7,4MB) → AES-GCM → base64 lần 2 trong payload (+33% nữa → 9,97MB). Khi mở: `atob` ~10MB → PBKDF2 → decrypt → `document.write` chuỗi 7,4MB **parse đồng bộ trên main thread** (treo UI 1-3 giây trên máy yếu; Chrome cũng log cảnh báo deprecated với document.write cỡ này); full-text search index thêm ~15-20MB RAM khi kích hoạt.

**Fix đáng làm nếu còn phát triển tiếp:** gzip nội dung trước khi mã hóa (thêm 5 dòng Python), giải nén phía browser bằng `DecompressionStream('gzip')` (Chrome/Edge/Firefox/Safari hiện đại đều hỗ trợ) → index.html ước còn ~2,5-3MB, mở nhanh hơn đáng kể.

### 2.4. Trang khóa phụ thuộc mạng ngoài

Google Fonts (3 family) + ảnh nền Unsplash hotlink. Offline vẫn hoạt động (font fallback, nền gradient), nhưng mỗi lần mở đều gọi ra ngoài, và link ảnh Unsplash có thể chết bất kỳ lúc nào. Với file "tự chứa" thì nên nhúng ảnh base64 + bỏ webfont ở riêng trang khóa.

### 2.5. Không có noscript, số liệu tĩnh sai

JS tắt → trang trắng hoàn toàn, không một dòng thông báo (không có `<noscript>`). Trong shell, `docCount/pmTotal/tbTotal` hardcode "15" trong HTML tĩnh — JS cập nhật thành 24 ngay sau đó, nhưng là vết tích của bản 15 file cũ, và sẽ hiển thị sai nếu script lỗi giữa chừng.

### 2.6. Triển khai: mật khẩu chỉ có nghĩa khi phân phối ĐÚNG MỘT file

Trong cùng thư mục đang tồn tại song song: `index.html` (mã hóa) = `masterclass-protected.html` (mã hóa, trùng vai trò, ~10MB mỗi bản) + `masterclass-all-in-one.html` (KHÔNG mã hóa) + 24 file nguồn không mã hóa + 3 thư mục backup. Nếu quy trình chia sẻ là copy/deploy cả thư mục thì lớp mật khẩu vô nghĩa. Chỉ nên phân phối duy nhất `index.html`; cân nhắc bỏ một trong hai bản mã hóa trùng nhau.

### 2.7. Các điểm nhỏ

- Tiến độ học lưu `localStorage` theo origin trình duyệt: đổi máy/trình duyệt/khác đường dẫn origin là mất; không có export/import tiến độ.
- Chỉ lưu "bài đang mở", không lưu vị trí cuộn trong bài.
- `make-protected.py` nhận mật khẩu qua argv → lộ trong shell history/process list; nên chuyển sang `getpass`.
- Mỗi lần refresh phải nhập lại mật khẩu + chạy lại PBKDF2 (không cache key trong `sessionStorage`) — có thể là chủ đích, nhưng đáng ghi nhận.

## 3. Những gì làm ĐÚNG (để khỏi sửa nhầm)

- Crypto chuẩn: GCM có authentication, salt/IV ngẫu nhiên mỗi build, iterations cao.
- 24/24 file con đều có `<head>` → GUARD inject đúng vị trí, không file nào rơi vào nhánh quirks-mode.
- Không có cross-file link (`href="16-...html"`) trong 24 bài → không có link gãy kiểu đó trong iframe (xref chỉ nằm ở `00-index.html`, vốn không được đóng gói).
- Metadata (label/full/group) được escape đúng ở mọi điểm render (textContent hoặc esc()) — không có kênh XSS từ metadata; build.py có guard chống chuỗi `</script` trong JSON.
- Kiến trúc iframe srcdoc cô lập CSS/JS của 24 bài — quyết định đúng, tránh được xung đột style khi gộp.

## 4. Thứ tự ưu tiên sửa

1. **1.4** — `<base target="_blank">` trong GUARD (1 dòng, sửa trải nghiệm đọc rõ rệt nhất).
2. **1.6** — chain make-protected.py vào .bat (chặn tái diễn lỗi bản mã hóa lỗi thời).
3. **1.5** — gom group khi render hoặc đổi group 23/24 (sửa xong phải chạy lại build + mã hóa).
4. **1.2 + 1.3** — chip 24 + phân biệt lỗi môi trường vs sai mật khẩu.
5. **1.1** — quyết định một lần: passphrase dài (bảo mật thật) hay giữ PIN (khóa lịch sự).
6. **2.1** — nới copy cho khối code nếu muốn người học chạy lab.
7. **2.3** — gzip trước mã hóa (tùy chọn, lợi nhất nếu còn gửi file cho nhiều người).
