import sys
import os
import asyncio
import threading
import tempfile
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QGridLayout, QFileDialog, QComboBox, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from ultralytics import YOLO
import cv2
from telegram import Bot

model_path = r"C:\Users\magic\Desktop\Nghiên_cứu_khoa_học\Fall_Detection_Using_Yolov8-main\model\fall_detection.pt"

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

TOKEN = '7533715892:AAEznW0oScW2u5_tYIsYxGpppwdwJ4QS_AU'
CHAT_ID = '-4570371594'
rtsp_url = "rtsp://admin:123456789tung@192.168.0.110:554/ch1/main"


class VideoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.device = 'GPU'
        self.model = self.load_model()
        self.bounding_box_visible = True
        self.output_path = ""
        self.detect_enabled = True
        self.auto_message_enabled = False
        self.auto_save_enabled = False

        # Initialize counts
        self.saved_image_count = 0
        self.sent_message_count = 0

        # UI Elements
        self.info_label = QLabel(self)
        self.cap = cv2.VideoCapture(rtsp_url)

        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.toggle_detect()

    def initUI(self):
        self.setWindowTitle("Fall Detection 2024")
        self.setStyleSheet("background-color: #EDEDED; font-family: Arial;")

        layout = QVBoxLayout()
        self.label = QLabel(self)
        layout.addWidget(self.label)

        self.path_label = QLabel("Chưa có đường dẫn lưu trữ", self)
        self.path_label.setFixedHeight(35)
        self.path_label.setStyleSheet(self.get_label_style())
        layout.addWidget(self.path_label)

        self.object_count_label = QLabel(self)
        self.object_count_label.setStyleSheet(self.get_label_style())
        layout.addWidget(self.object_count_label)

        self.saved_images_label = QLabel("Số lượng ảnh đã lưu: 0", self)
        self.saved_images_label.setStyleSheet(self.get_label_style())
        layout.addWidget(self.saved_images_label)

        self.sent_messages_label = QLabel("Số lượng tin nhắn đã gửi: 0", self)
        self.sent_messages_label.setStyleSheet(self.get_label_style())
        layout.addWidget(self.sent_messages_label)

        self.device_combo = QComboBox(self)
        self.device_combo.addItems(["GPU", "CPU"])
        self.device_combo.setStyleSheet(self.get_combo_style())
        self.device_combo.currentIndexChanged.connect(
            self.change_detection_device)
        layout.addWidget(self.device_combo)

        layout.setSpacing(10)

        button_layout = QGridLayout()
        button_layout.setSpacing(10)
        self.setup_buttons(button_layout)
        layout.addLayout(button_layout)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.setGeometry(100, 100, 1280, 720)

    def setup_buttons(self, layout):
        self.toggle_button = QPushButton("Tắt Bounding Box", self)
        self.toggle_button.setStyleSheet(
            self.get_button_style(self.bounding_box_visible))
        self.toggle_button.clicked.connect(self.toggle_bounding_box)
        layout.addWidget(self.toggle_button, 0, 0)

        save_button = QPushButton("Chọn Đường Dẫn", self)
        save_button.setStyleSheet(self.get_button_style(False))
        save_button.clicked.connect(self.save_path)
        layout.addWidget(save_button, 0, 1)

        open_button = QPushButton("Mở Đường Dẫn", self)
        open_button.setStyleSheet(self.get_button_style(False))
        open_button.clicked.connect(self.open_path)
        layout.addWidget(open_button, 0, 2)

        self.detect_button = QPushButton("Bật Chế Độ Phát Hiện", self)
        self.detect_button.setStyleSheet(
            self.get_button_style(self.detect_enabled))
        self.detect_button.clicked.connect(self.toggle_detect)
        layout.addWidget(self.detect_button, 1, 1)

        self.auto_message_button = QPushButton(
            "Bật Gửi Tin Nhắn Tự Động", self)
        self.auto_message_button.setStyleSheet(self.get_button_style(False))
        self.auto_message_button.clicked.connect(self.toggle_auto_message)
        layout.addWidget(self.auto_message_button, 1, 0)

        self.auto_save_button = QPushButton("Bật Lưu Ảnh Tự Động", self)
        self.auto_save_button.setStyleSheet(self.get_button_style(False))
        self.auto_save_button.clicked.connect(self.toggle_auto_save)
        layout.addWidget(self.auto_save_button, 1, 2)

    def get_button_style(self, is_enabled):
        if is_enabled:
            return """
                QPushButton {
                    border-radius: 20px;
                    background-color: #4CAF50;
                    color: white;
                    font-size: 16px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """
        else:
            return """
                QPushButton {
                    border-radius: 20px;
                    background-color: #f44336;
                    color: white;
                    font-size: 16px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #e53935;
                }
            """

    def get_label_style(self):
        return """
            QLabel {
                font-size: 18px;
                padding: 10px;
                border: 1px solid #4CAF50;
                border-radius: 10px;
                background-color: #ffffff;
                color: #333333;
            }
        """

    def get_combo_style(self):
        return """
            QComboBox {
                border-radius: 10px;
                background-color: #ffffff;
                padding: 10px;
                font-size: 16px;
            }
        """

    def load_model(self):
        model = YOLO(model_path).cuda(0 if self.device == 'GPU' else 0)
        print(f"Mô hình được tải: {model_path}")
        return model

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
        self.toggle_button.setStyleSheet(
            self.get_button_style(self.bounding_box_visible))

    def save_path(self):
        selected_directory = QFileDialog.getExistingDirectory(
            self, "Chọn đường dẫn lưu trữ")
        if selected_directory:
            self.output_path = selected_directory
            self.path_label.setText(f"Đường dẫn lưu trữ: {self.output_path}")
            self.info_label.setText("Đường dẫn đã được lưu thành công!")
        else:
            self.info_label.setText("Không có đường dẫn nào được chọn.")

    def open_path(self):
        if self.output_path:
            os.startfile(self.output_path)

    def toggle_detect(self):
        self.detect_enabled = not self.detect_enabled
        self.detect_button.setText(
            "Tắt Chế Độ Phát Hiện" if self.detect_enabled else "Bật Chế Độ Phát Hiện")
        self.detect_button.setStyleSheet(
            self.get_button_style(self.detect_enabled))

    def toggle_auto_message(self):
        self.auto_message_enabled = not self.auto_message_enabled
        self.auto_message_button.setText(
            "Tắt Gửi Tin Nhắn Tự Động" if self.auto_message_enabled else "Bật Gửi Tin Nhắn Tự Động")
        self.auto_message_button.setStyleSheet(
            self.get_button_style(self.auto_message_enabled))

    def toggle_auto_save(self):
        if not self.output_path:
            QMessageBox.warning(
                self, "Cảnh Báo", "Vui lòng chọn đường dẫn lưu trữ trước khi bật chế độ lưu ảnh tự động.")
            return

        self.auto_save_enabled = not self.auto_save_enabled
        self.auto_save_button.setText(
            "Tắt Lưu Ảnh Tự Động" if self.auto_save_enabled else "Bật Lưu Ảnh Tự Động")
        self.auto_save_button.setStyleSheet(
            self.get_button_style(self.auto_save_enabled))

    async def send_message(self, token, chat_id, message, image_path):
        bot = Bot(token=token)
        with open(image_path, 'rb') as photo:
            await bot.send_photo(chat_id=chat_id, photo=photo, caption=message)
        self.sent_message_count += 1
        self.sent_messages_label.setText(
            f"Số lượng tin nhắn đã gửi: {self.sent_message_count}")

    def update_frame(self):
        if not self.cap.isOpened():
            print("Không thể mở luồng video!")
            return

        success, frame = self.cap.read()
        if not success:
            print("Không thể đọc khung hình!")
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (1280, 720))

        if self.detect_enabled and self.model is not None:
            results = self.model.track(frame, persist=True, conf=0.75)
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

                # Automatic message sending
                if self.auto_message_enabled:
                    temp_file = tempfile.NamedTemporaryFile(
                        delete=False, suffix='.jpg')
                    cv2.imwrite(temp_file.name, cv2.cvtColor(
                        annotated_frame, cv2.COLOR_RGB2BGR))

                    thread = threading.Thread(target=asyncio.run, args=(self.send_message(TOKEN, CHAT_ID,
                                                                                          "Phát hiện có người bị ngã trong khung hình!", temp_file.name),))
                    thread.start()
                    temp_file.close()

                # Automatic image saving
                if self.auto_save_enabled and self.output_path:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_path = os.path.join(
                        self.output_path, f"detected_{timestamp}.jpg")
                    cv2.imwrite(save_path, cv2.cvtColor(
                        annotated_frame, cv2.COLOR_RGB2BGR))
                    self.saved_image_count += 1
                    self.saved_images_label.setText(
                        f"Số lượng ảnh đã lưu: {self.saved_image_count}")
                    print(f"Ảnh đã được lưu: {save_path}")

        height, width, channel = annotated_frame.shape
        bytes_per_line = 3 * width
        q_img = QImage(annotated_frame.data, width, height,
                       bytes_per_line, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(q_img))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = VideoApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
