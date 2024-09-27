from ultralytics import YOLO

model_weights_path = r"C:\Users\magic\Desktop\Nghiên_cứu_khoa_học\Fall_Detection_Using_Yolov8-main\model\fall_detection.pt"

all_objects_model = YOLO(model_weights_path)

# Display model architecture
print("Model Architecture:")
print(all_objects_model.model)

# Display input size
print("\nInput Size:")
print(all_objects_model.model.stride)

# Display class names
print("\nClass Names:")
print(all_objects_model.names)
