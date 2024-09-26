import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QGridLayout, QFileDialog, QComboBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from ultralytics import YOLO
import cv2
from datetime import datetime
import asyncio
from telegram import Bot

TOKEN = 'YOUR_TOKEN_HERE'
CHAT_ID = 'YOUR_CHAT_ID_HERE'

rtsp_url = "rtsp://admin:123456789tung@192.168.0.110:554/ch1/main"
model_directory = r"C:\Users\magic\Desktop\Nghiên_cứu_khoa_học\Fall_Detection_Using_Yolov8-main\model"

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


class VideoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.device = 'GPU'
        self.model = None
        self.bounding_box_visible = True
        self.output_path = ""
        self.auto_save_enabled = False
        self.detect_enabled = True
        self.message_enabled = False
        self.info_label = QLabel(self)
        self.info_label.setStyleSheet("font-size: 16px;")
        self.cap = cv2.VideoCapture(rtsp_url)

        self.initUI()  # #MARK: Initialize UI components
        self.load_models()  # #MARK: Load detection models
        self.timer = QTimer()
        # #MARK: Connect timer for video updates
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def initUI(self):
        self.setWindowTitle("Fall Detection 2024")
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

        # Device Selection Dropdown
        self.device_combo = QComboBox(self)
        self.device_combo.addItems(["GPU", "CPU"])
        self.device_combo.currentIndexChanged.connect(
            self.change_detection_device)  # #MARK: Change detection device
        self.device_combo.setStyleSheet(self.get_combobox_style())
        layout.addWidget(self.device_combo)

        # Model Selection Dropdown
        self.model_combo = QComboBox(self)
        self.model_combo.setStyleSheet(self.get_combobox_style())
        layout.addWidget(QLabel("Chọn mô hình:", self))
        layout.addWidget(self.model_combo)

        button_layout = QGridLayout()
        button_layout.setSpacing(15)
        self.setup_buttons(button_layout)  # #MARK: Setup action buttons
        layout.addLayout(button_layout)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.setGeometry(100, 100, 1280, 720)

    def get_combobox_style(self):
        return """
            QComboBox {
                background-color: #f0f0f0; 
                color: #333; 
                border: 2px solid #007BFF; 
                border-radius: 8px; 
                padding: 5px; 
                font-size: 14px; 
            }
            QComboBox:hover {
                border: 2px solid #0056b3; 
            }
        """

    def setup_buttons(self, layout):
        button_styles_enabled = """
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

        self.toggle_button = QPushButton("Tắt Bounding Box", self)
        self.toggle_button.setStyleSheet(button_styles_enabled)
        # #MARK: Toggle bounding box visibility
        self.toggle_button.clicked.connect(self.toggle_bounding_box)
        layout.addWidget(self.toggle_button, 0, 0)

        save_button = QPushButton("Chọn Đường Dẫn", self)
        save_button.setStyleSheet(button_styles_enabled)
        # #MARK: Save path selection
        save_button.clicked.connect(self.save_path)
        layout.addWidget(save_button, 0, 1)

        open_button = QPushButton("Mở Đường Dẫn", self)
        open_button.setStyleSheet(button_styles_enabled)
        # #MARK: Open selected path
        open_button.clicked.connect(self.open_path)
        layout.addWidget(open_button, 0, 2)

        self.auto_save_button = QPushButton("Bật Lưu Tự Động", self)
        self.auto_save_button.setStyleSheet(button_styles_enabled)
        self.auto_save_button.clicked.connect(
            self.toggle_auto_save)  # #MARK: Toggle auto-save
        layout.addWidget(self.auto_save_button, 1, 0)

        self.detect_button = QPushButton("Bật Chế Độ Phát Hiện", self)
        self.detect_button.setStyleSheet(button_styles_enabled)
        self.detect_button.clicked.connect(
            self.toggle_detect)  # #MARK: Toggle detection mode
        layout.addWidget(self.detect_button, 1, 1)

        self.message_button = QPushButton("Bật Gửi Tin Nhắn", self)
        self.message_button.setStyleSheet(button_styles_enabled)
        self.message_button.clicked.connect(
            self.toggle_message)  # #MARK: Toggle message sending
        layout.addWidget(self.message_button, 1, 2)

    def load_models(self):
        models = [f for f in os.listdir(model_directory) if f.endswith('.pt')]
        self.model_combo.addItems(models)
        self.model_combo.currentIndexChanged.connect(
            self.change_model)  # #MARK: Change selected model

    def change_model(self):
        selected_model = self.model_combo.currentText()
        if selected_model:
            self.model = YOLO(os.path.join(model_directory, selected_model)).cuda(
                0 if self.device == 'GPU' else 0)
            print(f"Mô hình được chọn: {selected_model}")

    def change_detection_device(self):
        selected_device = self.device_combo.currentText()
        if selected_device == "GPU":
            if self.model is not None:
                self.model = self.model.cuda(0)
            self.device = 'GPU'
        else:
            if self.model is not None:
                self.model = self.model.cpu()
            self.device = 'CPU'
        print(f"Detection device set to: {self.device}")

    def toggle_bounding_box(self):
        self.bounding_box_visible = not self.bounding_box_visible
        self.toggle_button.setText(
            "Tắt Bounding Box" if self.bounding_box_visible else "Bật Bounding Box")

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
            "Tắt Lưu Tự Động" if self.auto_save_enabled else "Bật Lưu Tự Động")

    def toggle_detect(self):
        self.detect_enabled = not self.detect_enabled
        self.detect_button.setText(
            "Tắt Chế Độ Phát Hiện" if self.detect_enabled else "Bật Chế Độ Phát Hiện")

    def toggle_message(self):
        if not self.auto_save_enabled or not self.output_path:
            self.message_enabled = False
            self.message_button.setText(
                "Bật Gửi Tin Nhắn (Cần chọn đường dẫn và bật lưu tự động)")
            return

        self.message_enabled = not self.message_enabled
        self.message_button.setText(
            "Tắt Gửi Tin Nhắn" if self.message_enabled else "Bật Gửi Tin Nhắn")

    def update_frame(self):
        if not self.cap.isOpened():
            print("Không thể mở luồng video!")
            return

        success, frame = self.cap.read()
        if not success:
            print("Không thể đọc khung hình!")
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (640, 480))

        if self.detect_enabled and self.model is not None:
            # #MARK: Run detection model
            results = self.model.track(frame, persist=True, conf=0.6)
        else:
            results = [None]

        annotated_frame = frame
        if results[0] is not None:
            annotated_frame = results[0].plot(
            ) if self.bounding_box_visible else frame
            object_count = len(results[0].boxes)

            if object_count > 0:
                self.object_count_label.setText(
                    f"Đã nhận diện {object_count} vật thể")

                if any(self.model.names[int(box.cls[0])] == "person" for box in results[0].boxes):
                    if self.message_enabled and self.auto_save_enabled and self.output_path:
                        # #MARK: Send alert if person detected
                        asyncio.create_task(self.send_alert(annotated_frame))

        height, width, channel = annotated_frame.shape
        bytes_per_line = 3 * width
        q_img = QImage(annotated_frame.data, width, height,
                       bytes_per_line, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(q_img))

        if self.auto_save_enabled and results[0] and len(results[0].boxes) > 0:
            # #MARK: Auto-save detected frames
            self.save_image(annotated_frame)

    async def send_message(self, token, chat_id, message, image_path):
        bot = Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=message)
        if image_path:
            with open(image_path, 'rb') as photo:
                await bot.send_photo(chat_id=chat_id, photo=photo)

    async def send_alert(self, frame):
        if not self.output_path:
            self.info_label.setText("Vui lòng chọn đường dẫn lưu trữ trước!")
            return

        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        image_path = os.path.join(
            self.output_path, f"alert_frame_{current_time}.jpg")
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(image_path, frame_bgr)

        # #MARK: Send alert message with image
        await self.send_message(TOKEN, CHAT_ID, "Phát hiện có người bị ngã!", image_path)

    def closeEvent(self, event):
        self.cap.release()
        event.accept()  # Gọi accept để đóng ứng dụng


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoApp()
    window.show()
    sys.exit(app.exec_())
