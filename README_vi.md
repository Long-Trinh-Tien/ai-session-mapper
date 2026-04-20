<div align="center">
  <h1>🔍 AI Session Mapper</h1>
  <p><strong>Không bao giờ làm mất code sinh ra từ AI nữa.</strong></p>
  <p>Một công cụ CLI nhẹ gọn, độc lập để càn quét, giải mã và hiển thị tất cả các phiên làm việc ẩn của các AI Agentic (Gemini CLI & Opencode) về dạng đường dẫn dễ đọc.</p>
  
  [![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
  
  [Tiếng Việt](README_vi.md) • [English](README.md)
</div>

---

## 🎯 Vấn Đề (The Pain Point)

Khi bạn sử dụng các trợ lý lập trình như **Gemini CLI** hay **Opencode**, chúng lưu vết phiên làm việc (workspace sessions) của bạn ẩn sâu bên trong thư mục hệ thống (AppData). Tệ hơn, đường dẫn thường bị mã hóa base64 hoặc rút gọn rất khó đọc.

*Đã bao giờ bạn tìm lại một prototype xịn xò tạo ra từ 3 hôm trước nhưng chẳng nhớ nó nằm ở folder nào?*

**AI Session Mapper** được sinh ra để giải quyết nỗi đau này! Tool sục sạo tận cùng thư mục `~/.gemini` và `%APPDATA%\ai.opencode.desktop`, giải mã các cấu trúc dự án và hiển thị ra một bảng log siêu xịn ngay trên Terminal của bạn.

## ✨ Tính Năng Nổi Bật

*   **Không cần thư viện ngoài:** Viết 100% bằng Python Script cơ bản. Tải về là xài.
*   **Giải Mã Opencode:** Đào sâu vào `opencode.global.dat` chứ không dựa vào tên file `.dat` bị băm nát để trích xuất ra **đường dẫn gốc hoàn chỉnh**.
*   **Gemini Tracker:** Tự động parse JSON map lồng ghép vô cùng phức tạp của `projects.json`.
*   **Bảng Thống Kê Chung:** Hiển thị Tên Agent, Session Name (thư mục hiện tại), Đường Dẫn Tuyệt Đối và Thời Gian.
*   **Tương thích mọi thiết bị:** Fix triệt để mọi lỗi Unicode do Emoji gây ra trên những máy ảo Windows, PowerShell hoặc môi trường thiếu font.

## 🚀 Cài Đặt & Sử Dụng

### Cách 1: Chạy trực tiếp bằng Python

```cmd
cd cli
python session_mapper.py
```

### Cách 2: Biên dịch thành file `.exe` chạy độc lập (Dành cho Windows)

Mẹo siêu xịn: Bạn có thể gói gọn toàn bộ script bằng `PyInstaller` thành một file binary `.exe` duy nhất. Không cần cài Python ở máy đích vẫn có thể chạy!

1. Cài đặt thư viện PyInstaller:
   ```cmd
   pip install pyinstaller
   ```
2. Đóng gói thành 1 file:
   ```cmd
   pyinstaller --onefile --name last_session session_mapper.py
   ```
3. Lấy file hệ thống của bạn tại:
   ```cmd
   dist/last_session.exe
   ```
Giờ thì bạn có thể copy `last_session.exe` vào thẳng thư mục hệ thống (ví dụ: `C:\Users\TenBan\AppData\Local\OpenCode`) và chỉ việc ấn chạy mà thôi!

## 📋 Kết Quả Ví Dụ

```text
[i] Scanning for AI Agent Logging Sessions (Gemini & Opencode)...
-----------------------------------------------------------------------------------------------------
| Agent      | Session Name       | Project Directory                                | Last Active  |
-----------------------------------------------------------------------------------------------------
| Gemini     | nextjs-dashboard   | /Users/dev/workspace/nextjs-dashboard            | Unknown      |
| Opencode   | awesome-app        | C:\Projects\awesome-app                          | 1d ago       |
| Opencode   | data-analyzer      | C:\Projects\data-analyzer                        | 1h ago       |
-----------------------------------------------------------------------------------------------------
```

## 🛠 Cách Hoạt Động (Under the hood)

*   **Gemini CLI:** Tool sẽ lấy thông tin đường dẫn gốc từ file `projects.json` (chú ý bắt cả field `projects` nếu có), sau đó tham chiếu chéo với thư mục `sessions/` bằng cách query *modification time* của ID tương ứng.
*   **Opencode:** Tool thâm nhập vào file `%APPDATA%/ai.opencode.desktop/opencode.global.dat`, bóc tách chuỗi JSON `globalSync.project` lưu dưới dạng nhúng, qua đó đánh bại hoàn toàn cơ chế ẩn file rút gọn của Opencode, lấy thẳng Full Path an toàn tuyệt đối.

## 📄 Bản Quyền
Giấy phép MIT. Sẵn sàng cho mọi mở rộng!
