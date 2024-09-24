import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QFileDialog, QGridLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from ultralytics import YOLO
import cv2
import os
from datetime import datetime
import asyncio
from telegram import Bot

TOKEN = '7533715892:AAEznW0oScW2u5_tYIsYxGpppwdwJ4QS_AU'
CHAT_ID = '-4570371594'

rtsp_url = "rtsp://admin:123456789tung@192.168.0.110:554/ch1/main"

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


class VideoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.model = YOLO("yolov8n.pt")
        self.bounding_box_visible = True
        self.output_path = ""
        self.auto_save_enabled = False
        self.detect_enabled = True
        self.message_enabled = False
        self.info_label = QLabel(self)
        self.info_label.setStyleSheet("font-size: 16px;")
        self.cap = cv2.VideoCapture(0)
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def initUI(self):
        self.setWindowTitle("Fall Detection 2024")
        # Light cyan background
        self.setStyleSheet("background-color: #e0f7fa;")

        layout = QVBoxLayout()

        self.label = QLabel(self)
        layout.addWidget(self.label)

        self.path_label = QLabel("Chưa có đường dẫn lưu trữ", self)
        self.path_label.setFixedWidth(300)
        self.path_label.setStyleSheet(
            "font-size: 14px; padding: 10px; border: 2px solid #4CAF50; border-radius: 10px; "
            "background-color: #ffffff; color: #333333;"
        )
        layout.addWidget(self.path_label)

        self.object_count_label = QLabel(self)
        self.object_count_label.setStyleSheet(
            "font-size: 16px; color: #00796b; padding: 5px;")
        layout.addWidget(self.object_count_label)

        button_layout = QGridLayout()
        button_layout.setSpacing(15)

        # Define button styles for enabled and disabled states
        self.button_styles_enabled = """
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                border: none; 
                border-radius: 10px; 
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """

        self.button_styles_disabled = """
            QPushButton {
                background-color: #f44336; 
                color: white; 
                border: none; 
                border-radius: 10px; 
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
        """

        self.toggle_button = QPushButton("Tắt Bounding Box", self)
        self.toggle_button.setStyleSheet(self.button_styles_enabled)
        self.toggle_button.clicked.connect(self.toggle_bounding_box)
        button_layout.addWidget(self.toggle_button, 0, 0)

        save_button = QPushButton("Chọn Đường Dẫn", self)
        save_button.setStyleSheet(self.button_styles_enabled)
        save_button.clicked.connect(self.save_path)
        button_layout.addWidget(save_button, 0, 1)

        open_button = QPushButton("Mở Đường Dẫn", self)
        open_button.setStyleSheet(self.button_styles_enabled)
        open_button.clicked.connect(self.open_path)
        button_layout.addWidget(open_button, 0, 2)

        self.auto_save_button = QPushButton("Bật Lưu Tự Động", self)
        self.auto_save_button.setStyleSheet(self.button_styles_enabled)
        self.auto_save_button.clicked.connect(self.toggle_auto_save)
        button_layout.addWidget(self.auto_save_button, 1, 0)

        self.detect_button = QPushButton("Bật Chế Độ Phát Hiện", self)
        self.detect_button.setStyleSheet(self.button_styles_enabled)
        self.detect_button.clicked.connect(self.toggle_detect)
        button_layout.addWidget(self.detect_button, 1, 1)

        self.message_button = QPushButton("Bật Gửi Tin Nhắn", self)
        self.message_button.setStyleSheet(self.button_styles_enabled)
        self.message_button.clicked.connect(self.toggle_message)
        button_layout.addWidget(self.message_button, 1, 2)

        layout.addLayout(button_layout)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.setGeometry(100, 100, 1280, 720)

    def toggle_bounding_box(self):
        self.bounding_box_visible = not self.bounding_box_visible
        self.toggle_button.setText(
            "Tắt Bounding Box" if self.bounding_box_visible else "Bật Bounding Box"
        )
        self.toggle_button.setStyleSheet(
            self.button_styles_enabled if self.bounding_box_visible else self.button_styles_disabled)

    def save_path(self):
        selected_directory = QFileDialog.getExistingDirectory(
            self, "Chọn đường dẫn lưu trữ")
        if selected_directory:
            self.output_path = selected_directory
            self.path_label.setText(f"Đường dẫn lưu trữ: {self.output_path}")

    def open_path(self):
        if self.output_path:
            os.startfile(self.output_path)

    def toggle_auto_save(self):
        self.auto_save_enabled = not self.auto_save_enabled
        self.auto_save_button.setText(
            "Tắt Lưu Tự Động" if self.auto_save_enabled else "Bật Lưu Tự Động"
        )
        self.auto_save_button.setStyleSheet(
            self.button_styles_enabled if self.auto_save_enabled else self.button_styles_disabled)

    def toggle_detect(self):
        self.detect_enabled = not self.detect_enabled
        self.detect_button.setText(
            "Tắt Chế Độ Phát Hiện" if self.detect_enabled else "Bật Chế Độ Phát Hiện"
        )
        self.detect_button.setStyleSheet(
            self.button_styles_enabled if self.detect_enabled else self.button_styles_disabled)

    def toggle_message(self):
        self.message_enabled = not self.message_enabled
        self.message_button.setText(
            "Tắt Gửi Tin Nhắn" if self.message_enabled else "Bật Gửi Tin Nhắn"
        )
        self.message_button.setStyleSheet(
            self.button_styles_enabled if self.message_enabled else self.button_styles_disabled)

    def update_frame(self):
        success, frame = self.cap.read()
        if success:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 480))
            if self.detect_enabled:
                results = self.model.track(frame, persist=True, conf=0.6)
            else:
                results = [None]

            if results[0] is not None:
                annotated_frame = results[0].plot(
                ) if self.bounding_box_visible else frame
                object_count = len(results[0].boxes)

                if object_count > 0:
                    self.object_count_label.setText(
                        f"Đã nhận diện {object_count} vật thể")

                    # Kiểm tra xem có người bị ngã không
                    if any(self.model.names[int(box.cls[0])] == "person" for box in results[0].boxes):
                        if self.message_enabled:  # Chỉ gửi tin nhắn nếu bật
                            self.send_alert(annotated_frame)

            height, width, channel = annotated_frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(annotated_frame.data, width, height,
                           bytes_per_line, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(q_img))

            if self.auto_save_enabled and results[0] and len(results[0].boxes) > 0:
                self.save_image(annotated_frame)

    async def send_message(self, token, chat_id, message, image_path):
        bot = Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=message)
        with open(image_path, 'rb') as photo:
            await bot.send_photo(chat_id=chat_id, photo=photo)

    def send_alert(self, frame):
        if not self.output_path:
            self.info_label.setText("Vui lòng chọn đường dẫn lưu trữ trước!")
            return

        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        image_path = os.path.join(
            self.output_path, f"alert_frame_{current_time}.jpg")
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(image_path, frame_bgr)

        # Gửi tin nhắn và ảnh
        asyncio.run(self.send_message(TOKEN, CHAT_ID,
                    "Phát hiện có người bị ngã!", image_path))

    def send_alert(self, frame):
        # Gửi tin nhắn mà không lưu ảnh
        asyncio.run(self.send_message(TOKEN, CHAT_ID,
                    "Phát hiện có người bị ngã!", None))

    async def send_message(self, token, chat_id, message, image_path):
        bot = Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=message)
        if image_path:  # Only send photo if image_path is provided
            with open(image_path, 'rb') as photo:
                await bot.send_photo(chat_id=chat_id, photo=photo)

    def closeEvent(self, event):
        self.cap.release()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoApp()
    window.show()
    sys.exit(app.exec_())
