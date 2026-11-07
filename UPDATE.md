# Cập nhật Workflow3 từ repo

## 1. Lấy đúng phiên bản

Clone repo ra thư mục riêng, ví dụ `C:\Huy\etsy-workflow-updates`. Ghi lại `git rev-parse HEAD`; làm việc với cùng commit trong suốt lượt cập nhật. `LATEST.json` chứa phiên bản phân phối, mốc sổ lỗi, tên gói và SHA256. Gói này không tự cài hay tự kích hoạt.

Nếu không có Git, tải các file từ cùng một commit GitHub, không trộn file của nhiều mốc `main` khác nhau.

## 2. Kiểm gói

Tính SHA256 của `source.zip` bằng `Get-FileHash`. Giá trị phải khớp `LATEST.json` và `source-manifest.json`. Giải nén vào thư mục staging mới sau khi kiểm đường dẫn ZIP. Mỗi đường dẫn phải là file thông thường trong manifest, không có `..`, ổ đĩa tuyệt đối hoặc symlink. So đủ số file, kích thước và SHA256; không chấp nhận file lạ.

## 3. So với máy đang chạy

Đọc AGENTS.md và cấu hình thật ở máy nhận. Lập danh sách các file khác nhau, xác định tính năng cần cập nhật và phụ thuộc của chúng. Kiểm tra import/caller liên quan. Mọi đường dẫn cố định như `C:/Huy/etsy-workflow` cần được đối chiếu với máy nhận. Giữ các thay đổi riêng chưa có trong repo.

Chỉ các file trong manifest được xem là nguồn có thể đồng bộ. Không xóa file local vì nó không nằm trong gói. Đặc biệt giữ toàn bộ `workspace`, `config/*.private.*`, thư viện artwork/guide riêng, credentials, browser profile và database n8n.

`config/listing-layout.json`, `config/kpi-layout.json` và `config/google-delivery.json` cũng là cấu hình riêng từng máy, dù tên không có `.private`. Chúng không có trong gói. Các file có `requires_local_binding_merge: true` trong manifest đã thay ID/link tài liệu máy nguồn bằng `LOCAL_BINDING_...` hoặc `LOCAL_DESTINATION_REQUIRED`. Giữ hoặc ánh xạ đích đúng của máy nhận khi merge; không chép placeholder vào tiến trình đang chạy rồi báo đã cài xong.

Một số config chung tham chiếu file guide/ảnh chuẩn không có trong gói. Giữ các file chuẩn đã thiết lập ở máy nhận và xác minh hash theo manifest mẻ của chính máy đó. Không dùng đường dẫn máy nguồn làm bằng chứng rằng máy nhận đã có file.

## 4. Sao lưu, kiểm tra, áp dụng

Sao lưu file bị tác động và lưu SHA trước/sau. Kiểm tra code trong staging trước khi thay file live. Với V53, sau khi có Playwright theo package-lock trong `scripts/flow-worker`, chạy:

```powershell
node --test scripts/flow-worker/flow-browser.test.cjs scripts/flow-worker/gologin.test.cjs scripts/flow-worker/runtime.test.cjs
```

Mốc phát hành đầu tiên đã qua **193 kiểm tra** trên máy nguồn. Tải lại đúng ảnh đã có qua GoLogin đã được kiểm chứng thật. Bước tìm ảnh hoàn chỉnh trước retry có kiểm thử hồi quy, chưa có lượt retry live mới sau bản sửa tại thời điểm phát hành. Đây không phải bảo đảm rằng máy nhận đã cài đủ hoặc đang chạy.

## 5. Kích hoạt và báo kết quả

Tuân thủ quyền và quy tắc restart của máy nhận. Không nhập đè database hay workflow n8n từ máy nguồn. Nếu thay đổi cần cấu hình graph n8n mà máy nhận chưa có, nêu rõ việc còn thiếu thay vì báo cập nhật hoàn tất. Không tự đăng nhập, đổi GoLogin profile, duyệt ảnh hay chạy mẻ để thử.

Sau khi áp dụng, kiểm health và checkpoint của đúng thành phần. Ghi phiên bản phân phối + commit vào biên bản cập nhật local. Báo phần code đã cập nhật, phần đã nạp vào tiến trình và phần còn chờ người dùng riêng biệt.
