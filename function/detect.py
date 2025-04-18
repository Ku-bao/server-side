import cv2
from ultralytics import YOLO

# Load the YOLO model
# model = YOLO("yolo11n_ncnn_model")
model = YOLO("best_openvino_model")
# model = YOLO("yolo11n.onnx")
# model = YOLO("best_ncnn_model")
# model = YOLO("best.pt")

# Open the video file (use 0 for the default camera)
cap = cv2.VideoCapture(0)

# Initialize variables for FPS calculation
prev_time = 0

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Get the current time (for FPS calculation)
        current_time = cv2.getTickCount()
        
        # Calculate the time difference (in seconds)
        time_diff = (current_time - prev_time) / cv2.getTickFrequency()
        
        # Calculate FPS
        fps = 1 / time_diff if time_diff > 0 else 0

        # Update the previous time
        prev_time = current_time
        
        # Run YOLO inference on the frame
        results = model(frame, conf=0.65)

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the FPS on the frame
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(annotated_frame, f"FPS: {fps:.2f}", (10, 30), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Display the annotated frame
        cv2.imshow("YOLO Inference", annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()
