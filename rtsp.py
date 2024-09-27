from ultralytics import YOLO
import cv2
import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# Load the YOLO model
model = YOLO(
    r"C:\Users\magic\Desktop\Nghiên_cứu_khoa_học\Fall_Detection_Using_Yolov8-main\model\fall_detection.pt")

# Capture video from the RTSP stream
rtsp_url = "rtsp://admin:123456789tung@192.168.0.110:554/ch1/main"
cap = cv2.VideoCapture(rtsp_url)

# Set the window name
window_name = "YOLOv8 Tracking"

# Create a named window and set its size
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 1280, 720)

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLOv8 tracking on the frame, persisting tracks between frames
        results = model.track(frame, persist=True, conf=0.5)

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the annotated frame
        cv2.imshow(window_name, annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()
