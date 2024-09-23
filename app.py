import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from ultralytics import YOLO
import cv2
import os
from datetime import datetime

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


class VideoApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # MARK: Load YOLO Model
        self.model = YOLO("yolov8n.pt")
        self.bounding_box_visible = True
        self.output_path = ""
        self.auto_save_enabled = False
        self.detect_enabled = True
        self.info_label = QLabel(self)
        self.info_label.setStyleSheet("font-size: 16px;")

        # MARK: Capture Video
        self.cap = cv2.VideoCapture(0)

        # MARK: Set up the UI
        self.initUI()

        # MARK: Timer for Video Frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def initUI(self):
        self.setWindowTitle("Fall Detection 2024")
        self.setStyleSheet("background-color: #f0f0f5;")

        # MARK: Video Display Label
        self.label = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.label)

        # MARK: Path Label
        self.path_label = QLabel("Chưa có đường dẫn lưu trữ", self)
        self.path_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 5px;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                max-height: 25;
                overflow: hidden;  
                white-space: nowrap;  
                text-overflow: ellipsis;  
            }
        """)
        layout.addWidget(self.path_label)

        # MARK: Add object count label
        self.object_count_label = QLabel(self)
        self.object_count_label.setStyleSheet("font-size: 16px; color: blue;")
        layout.addWidget(self.object_count_label)

        # MARK: Button Layout
        button_layout = QHBoxLayout()

        # MARK: Toggle Bounding Box Button
        self.toggle_button = QPushButton("Tắt Bounding Box", self)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_bounding_box)
        button_layout.addWidget(self.toggle_button)

        # MARK: Choose Path Button
        save_button = QPushButton("Chọn Đường Dẫn", self)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #1E88E5;
            }
        """)
        save_button.clicked.connect(self.save_path)
        button_layout.addWidget(save_button)

        # MARK: Open Path Button
        open_button = QPushButton("Mở Đường Dẫn", self)
        open_button.setStyleSheet("""
            QPushButton {
                background-color: #FFC107;
                color: white;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #FFA000;
            }
        """)
        open_button.clicked.connect(self.open_path)
        button_layout.addWidget(open_button)

        # MARK: Auto-save Toggle Button
        self.auto_save_button = QPushButton("Bật Lưu Tự Động", self)
        self.auto_save_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                padding: 10px;
                border-radius: 8px;
            }
        """)
        self.auto_save_button.clicked.connect(self.toggle_auto_save)
        button_layout.addWidget(self.auto_save_button)

        # MARK: Detect Mode Toggle Button
        self.detect_button = QPushButton("Bật Chế Độ Phát Hiện", self)
        self.detect_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                padding: 10px;
                border-radius: 8px;
            }
        """)
        self.detect_button.clicked.connect(self.toggle_detect)
        button_layout.addWidget(self.detect_button)

        layout.addLayout(button_layout)

        # MARK: Central Widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # MARK: Set Window Size
        self.setGeometry(100, 100, 1280, 720)

    def toggle_bounding_box(self):
        self.bounding_box_visible = not self.bounding_box_visible
        if self.bounding_box_visible:
            self.toggle_button.setText("Tắt Bounding Box")
        else:
            self.toggle_button.setText("Bật Bounding Box")

    def save_path(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.Directory)
        selected_directory = file_dialog.getExistingDirectory(
            self, "Chọn đường dẫn lưu trữ")

        if selected_directory:
            self.output_path = selected_directory
            self.path_label.setText(f"Đường dẫn lưu trữ: {self.output_path}")

    def open_path(self):
        if self.output_path:
            os.startfile(self.output_path)

    def toggle_auto_save(self):
        self.auto_save_enabled = not self.auto_save_enabled
        if self.auto_save_enabled:
            self.auto_save_button.setText("Tắt Lưu Tự Động")
            self.auto_save_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;  /* Xanh khi bật */
                    color: white;
                    padding: 10px;
                    border-radius: 8px;
                }
            """)
        else:
            self.auto_save_button.setText("Bật Lưu Tự Động")
            self.auto_save_button.setStyleSheet("""
                QPushButton {
                    background-color: red;  /* Đỏ khi tắt */
                    color: white;
                    padding: 10px;
                    border-radius: 8px;
                }
            """)

    def toggle_detect(self):
        self.detect_enabled = not self.detect_enabled
        if self.detect_enabled:
            self.detect_button.setText("Tắt Chế Độ Phát Hiện")
            self.detect_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;  /* Xanh khi bật */
                    color: white;
                    padding: 10px;
                    border-radius: 8px;
                }
            """)
        else:
            self.detect_button.setText("Bật Chế Độ Phát Hiện")
            self.detect_button.setStyleSheet("""
                QPushButton {
                    background-color: red;  /* Đỏ khi tắt */
                    color: white;
                    padding: 10px;
                    border-radius: 8px;
                }
            """)

    def update_frame(self):
        success, frame = self.cap.read()
        if success:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if self.detect_enabled:
                results = self.model.track(frame, persist=True, conf=0.5)
            else:
                results = [None]

            if results[0] is not None:
                annotated_frame = results[0].plot(
                ) if self.bounding_box_visible else frame
                class_count = {}
                # Số lượng vật thể nhận diện được
                object_count = len(results[0].boxes)
                for box in results[0].boxes:
                    cls = int(box.cls[0])
                    class_name = self.model.names[cls]
                    conf = box.conf[0]
                    if class_name in class_count:
                        class_count[class_name] += 1
                    else:
                        class_count[class_name] = 1

                # Cập nhật label hiển thị tên class và số lượng vật thể
                class_info = "\n".join(
                    [f"{name}: {count} objects" for name, count in class_count.items()])
                self.info_label.setText(class_info)

                # Cập nhật label hiển thị số lượng tổng vật thể nhận diện được
                self.object_count_label.setText(
                    f"Đã nhận diện {object_count} vật thể")
            else:
                annotated_frame = frame
                self.info_label.clear()
                self.object_count_label.clear()

            height, width, channel = annotated_frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(annotated_frame.data, width, height,
                           bytes_per_line, QImage.Format_RGB888)

            self.label.setPixmap(QPixmap.fromImage(q_img))

            if self.auto_save_enabled and results[0] and len(results[0].boxes) > 0:
                self.save_image(annotated_frame)

    def save_image(self, frame):
        if self.output_path:
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            image_path = os.path.join(
                self.output_path, f"detected_frame_{current_time}.jpg")

            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(image_path, frame_bgr)
            print(f"Ảnh đã được lưu tại: {image_path}")

    def closeEvent(self, event):
        self.cap.release()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoApp()
    window.show()
    sys.exit(app.exec_())
