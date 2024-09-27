# Dự án Phát hiện té Ngã

Dự án này sử dụng YOLO để phát hiện ngã trong video từ camera. Ứng dụng có giao diện người dùng thân thiện cho phép bật/tắt chế độ phát hiện và gửi tin nhắn tự động qua Telegram.

## Nội dung

- [Yêu cầu](#yêu-cầu)
- [Cài đặt](#cài-đặt)
- [Cấu hình](#cấu-hình)
- [Chạy ứng dụng](#chạy-ứng-dụng)
- [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
- [Khắc phục sự cố](#khắc-phục-sự-cố)
- [Liên hệ](#liên-hệ)

## Yêu cầu

- Python 3.8 trở lên
- Thư viện cần thiết sẽ được cài đặt qua `requirements.txt`

## Cài đặt

### Bước 1: Cài đặt Python

Nếu chưa cài đặt Python, tải và cài đặt từ [trang chính thức của Python](https://www.python.org/downloads/). Đảm bảo chọn tùy chọn thêm Python vào PATH trong quá trình cài đặt.

### Bước 2: Tạo Môi trường Ảo

Mở terminal hoặc command prompt và chạy các lệnh sau:

```bash
# Cài đặt virtualenv nếu chưa cài
pip install virtualenv

# Tạo một môi trường ảo
virtualenv venv

# Kích hoạt môi trường ảo
# Trên Windows
venv\Scripts\activate
# Trên macOS/Linux
source venv/bin/activate

### Bước 3: Cài đặt Thư viện

pip install -r requirements.txt


1 .Đường dẫn mô hình: Đảm bảo đường dẫn tới mô hình YOLO (fall_detection.pt) là đúng trong mã. Nếu cần, thay đổi đường dẫn trong biến model_path:

2.Cấu hình Telegram Bot: Thay đổi TOKEN và CHAT_ID với thông tin của bot Telegram của bạn:
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
CHAT_ID = 'YOUR_CHAT_ID'

3. RTSP URL: Nếu bạn sử dụng camera khác, hãy cập nhật rtsp_url:
rtsp_url = "rtsp://username:password@camera_ip:port/ch1/main"

*Chạy lệnh sau trong terminal để khởi động ứng dụng*

python app.py

