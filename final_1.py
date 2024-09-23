from ultralytics import YOLO
import cv2
import os
import time
import asyncio
from telegram import Bot

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# Thay thế bằng token của bot của bạn
TOKEN = '7533715892:AAEznW0oScW2u5_tYIsYxGpppwdwJ4QS_AU'
# Thay thế bằng ID chat của bạn hoặc ID nhóm bạn muốn gửi tin nhắn
CHAT_ID = '-4570371594'

# Hàm gửi tin nhắn với ảnh


async def send_message_with_photo(token, chat_id, message, photo_path):
    bot = Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=message)
    await bot.send_photo(chat_id=chat_id, photo=open(photo_path, 'rb'))

# Load the YOLO model
model = YOLO("fall_det_1.pt")

# Capture video from the RTSP stream
rtsp_url = "rtsp://admin:123456789tung@192.168.0.110:554/ch1/main"
cap = cv2.VideoCapture(rtsp_url)

# Set the window name
window_name = "YOLOv8 Tracking"

# Create a named window and set its size
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 1280, 720)

# Đường dẫn lưu ảnh
# Thay đổi đường dẫn tại đây
save_directory = "C:/Users/magic/Desktop/Nghiên_cứu_khoa_học/Fall_Detection_Using_Yolov8-main/image"


# Kiểm tra và tạo thư mục nếu chưa tồn tại
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLOv8 tracking on the frame, persisting tracks between frames
        results = model.track(frame, persist=True, conf=0.8)

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the annotated frame
        cv2.imshow(window_name, annotated_frame)

        # Kiểm tra số lượng đối tượng được phát hiện
        if len(results[0].boxes) > 0:
            # Tạo tên tệp cho ảnh với đường dẫn
            timestamp = int(time.time())
            filename = os.path.join(
                save_directory, f"captured_frame_{timestamp}.jpg")
            # Lưu ảnh
            cv2.imwrite(filename, frame)
            print(f"Đã lưu ảnh: {filename}")

            # Gửi tin nhắn với ảnh
            message = "Có người bị ngã ở đây nhé, đến đây!"
            asyncio.run(send_message_with_photo(
                TOKEN, CHAT_ID, message, filename))

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()
