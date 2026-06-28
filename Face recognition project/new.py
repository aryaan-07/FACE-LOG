
import cv2
import numpy as np
import time
try:
    import pandas as pd
except ModuleNotFoundError:
    pd = None
    print("Warning: 'pandas' is not installed; attendance will be stored using the csv module instead.")

try:
    import face_recognition
except ModuleNotFoundError:
    print("Error: The 'face_recognition' module is not installed. Please install it using 'pip install face-recognition'.")
    exit(1)
import os
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import threading
import queue

# Path to images folder
path = os.path.join(os.getcwd(), 'Images')
images = []
classNames = []

if not os.path.exists(path):
    os.makedirs(path)
    print("Place images in the 'Images' folder and restart the script.")
    exit(1)

# Load images and extract class names
myList = [f for f in os.listdir(path) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
for cl in myList:
    curImg = cv2.imread(os.path.join(path, cl))
    if curImg is not None:
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])

all_roll_numbers = set(classNames)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)
        if encodings:
            encodeList.append(encodings[0])
    return encodeList

encodeListKnown = findEncodings(images)

def markAttendance(name):
    today_date = datetime.now().strftime('%Y-%m-%d')
    file_path = 'Attendance.csv'
    # If pandas is available, use it for convenience
    if pd is not None:
        columns = ['Name', 'Date']
        df = pd.read_csv(file_path) if os.path.exists(file_path) else pd.DataFrame(columns=columns)
        if not ((df['Name'] == name) & (df['Date'] == today_date)).any():
            df = pd.concat([df, pd.DataFrame({'Name': [name], 'Date': [today_date]})], ignore_index=True)
            df.to_csv(file_path, index=False)
        return

    # Fallback implementation using csv module when pandas is not installed
    import csv
    if not os.path.exists(file_path):
        # create file with header
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Name', 'Date'])
            writer.writeheader()

    already_present = False
    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Name') == name and row.get('Date') == today_date:
                already_present = True
                break

    if not already_present:
        with open(file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Name', 'Date'])
            writer.writerow({'Name': name, 'Date': today_date})

class FaceRecognitionApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Face Recognition Attendance System")
        self.window.geometry("800x600")
        self.video_label = Label(window)
        self.video_label.pack()
        self.cap = cv2.VideoCapture(0)
        self.frame_queue = queue.Queue(maxsize=10)
        self.stop_event = threading.Event()
        self.recognition_running = False
        self.video_thread = threading.Thread(target=self.update_video_feed, daemon=True)
        self.video_thread.start()
        self.process_frames()

    def update_video_feed(self):
        frame_skip = 3
        frame_count = 0
        while not self.stop_event.is_set():
            ret, frame = self.cap.read()
            frame_count += 1
            if ret and frame_count % frame_skip == 0:
                frame = cv2.resize(frame, (240, 180))
                if not self.frame_queue.full():
                    self.frame_queue.put(frame)
            time.sleep(0.001)

    def process_frames(self):
        try:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb_frame)
                imgtk = ImageTk.PhotoImage(image=img)
                # keep a reference on the app instance to avoid GC and static-type warnings
                self.imgtk = imgtk
                self.video_label.configure(image=imgtk)
        finally:
            self.window.after(1, self.process_frames)

    def start_recognition(self):
        self.recognition_running = True
        self.present_students = set()
        threading.Thread(target=self.recognition_loop, daemon=True).start()

    def recognition_loop(self):
        while self.recognition_running:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_frame, model='hog')
                if face_locations:
                    encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                    for encodeFace, (top, right, bottom, left) in zip(encodings, face_locations):
                        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                        if faceDis.size > 0:
                            bestMatchIndex = np.argmin(faceDis)
                            if matches[bestMatchIndex] and faceDis[bestMatchIndex] < 0.5:
                                name = classNames[bestMatchIndex].upper()
                                self.present_students.add(name)
                                markAttendance(name)

    def stop_recognition(self):
        self.recognition_running = False

    def on_closing(self):
        self.stop_event.set()
        self.cap.release()
        self.window.destroy()

if __name__ == "__main__":
    root = Tk()
    app = FaceRecognitionApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
