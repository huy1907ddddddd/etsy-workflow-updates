# Workflow3 updates

Repo cập nhật mã nguồn Workflow3 cho Codex trên các máy khác.

**Bản phân phối đầu tiên: 2026.11.07.1. Mốc sổ lỗi: V53.** Phiên bản phân phối và số phiên bản trong sổ lỗi là hai trường riêng trong `LATEST.json`.

## Cho Codex ở máy nhận

Đọc [AGENTS.md](AGENTS.md), [LATEST.json](LATEST.json) và [UPDATE.md](UPDATE.md). Gói [source.zip](source.zip) chứa mã nguồn được phép đồng bộ; [source-manifest.json](source-manifest.json) ghi SHA256 của từng file. Git lưu lịch sử gói qua các commit.

Bạn có thể gửi cho Codex máy khác:

> Đọc https://github.com/huy1907ddddddd/etsy-workflow-updates/blob/main/AGENTS.md và LATEST.json trong cùng repo. So sánh với bản Workflow3 ở máy này, tải và kiểm SHA256 của source.zip, rồi cập nhật mã phù hợp theo UPDATE.md. Giữ nguyên tài khoản, cấu hình riêng, database, ảnh, checkpoint và quyền duyệt ở máy này. Không tự chạy lại mẻ hay sao chép môi trường máy nguồn. Báo rõ phần đã cập nhật và phần còn cần cấu hình.

## Nội dung hiện có

- Worker Flow, batch, text, KPI và dịch vụ duyệt web/bot cùng các module native liên quan.
- Prompt và quy tắc chung được chọn rõ trong bộ đóng gói.
- Chế độ prompt ra mockup áo thêu, luồng không dùng ảnh ánh xạ và adapter GoLogin local.
- Bản sửa V53: kiểm tra ảnh hoàn chỉnh trước Generate thử lại, giữ ảnh đã đặt tải khi có nhiều kết quả tương đương.

Đây là **gói mã để cập nhật một hệ thống Workflow3 đã có**, không phải bản sao đầy đủ để dựng máy mới. Không chứa workflow n8n đang lưu trong database, credentials, cấu hình `*.private.*`, tài khoản, profile, database, ảnh sản phẩm, thư viện chuẩn riêng hoặc trạng thái mẻ. Không có dịch vụ tự đẩy phiên bản hoặc tự cập nhật máy khác.

## Cho máy phát hành

Trong một bản clone của repo này:

```powershell
python -m unittest -v test_build_release.py
python build_release.py --source C:\Huy\etsy-workflow --version 2026.11.07.2 --register-version V53
git add README.md AGENTS.md UPDATE.md build_release.py test_build_release.py LATEST.json source-manifest.json source.zip .gitignore
git commit -m "Publish Workflow3 2026.11.07.2"
git push origin main
```

Chọn số phiên bản phân phối mới mỗi lần. Cập nhật ghi chú thay đổi và kết quả kiểm chứng trước khi push. Bộ đóng gói chỉ đọc thư mục chạy thật; nó không dừng worker, cập nhật n8n, ghi database hay khởi chạy mẻ.

Repo public để tải không cần đăng nhập. Quyền ghi repo vẫn thuộc chủ repo; không bật tự chạy mã hay triển khai từ pull request của người khác.
