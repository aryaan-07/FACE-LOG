import cv2

def find_available_cameras(max_index=5):
    available = []
    for i in range(max_index):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # Using DirectShow backend on Windows
        if cap.isOpened():
            print(f"Camera found at index {i}")
            available.append(i)
            cap.release()
    return available

print("Available cameras:", find_available_cameras())
