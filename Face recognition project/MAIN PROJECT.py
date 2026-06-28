import cv2
import numpy as np
import time
import pandas as pd
import os
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import threading
import winsound

try:
    import face_recognition
except ModuleNotFoundError:
    print("Error: Install face_recognition using 'pip install face-recognition'")
    exit(1)

# ---------------------- PATHS ----------------------
BASE_DIR = os.getcwd()
IMAGE_DIR = os.path.join(BASE_DIR, "Images")
MODEL_DIR = os.path.join(BASE_DIR, "models")

PROTO_PATH = os.path.join(MODEL_DIR, "deploy.prototxt")
MODEL_PATH = os.path.join(MODEL_DIR, "res10_300x300_ssd_iter_140000.caffemodel")

# ---------------------- CHECK DIRECTORIES ----------------------
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)
    print("Images folder created. Add images and restart program.")
    exit(1)

if not os.path.exists(PROTO_PATH) or not os.path.exists(MODEL_PATH):
    print("\nERROR: OpenCV DNN Model files not found!")
    print("Put these files in a folder named 'models':")
    print("1) deploy.prototxt")
    print("2) res10_300x300_ssd_iter_140000.caffemodel\n")
    exit(1)

# ---------------------- LOAD DNN MODEL ----------------------
print("Loading OpenCV DNN Face Detector...")
net = cv2.dnn.readNetFromCaffe(PROTO_PATH, MODEL_PATH)

# ---------------------- LOAD TRAINING IMAGES ----------------------
images = []
classNames = []

myList = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(("png", "jpg", "jpeg"))]

for file in myList:
    img_path = os.path.join(IMAGE_DIR, file)
    img = cv2.imread(img_path)

    if img is None:
        print(f"Warning: Could not load {file}")
        continue

    images.append(img)
    classNames.append(os.path.splitext(file)[0].upper())

all_roll_numbers = set(classNames)
print("Total Roll Numbers:", len(all_roll_numbers))

# ---------------------- ENCODING FUNCTION ----------------------
def findEncodings(images):
    encodeList = []
    for img in images:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb)

        if encodings:
            encodeList.append(encodings[0])
        else:
            print("Warning: No face found in training image. Skipping...")

    return encodeList

encodeListKnown = findEncodings(images)

if not encodeListKnown:
    print("Error: No face encodings found in Images folder.")
    exit(1)

print("Encoding Complete!")

# ---------------------- ATTENDANCE FUNCTION (FIXED) ----------------------
def markAttendance(name):
    today_date = datetime.now().strftime("%Y-%m-%d")
    file_name = "Attendance.csv"

    required_columns = ["Name", "Date"]

    if os.path.exists(file_name):
        try:
            df = pd.read_csv(file_name)

            if not all(col in df.columns for col in required_columns):
                df = pd.DataFrame(columns=required_columns)
            else:
                df = df[required_columns]

        except Exception:
            df = pd.DataFrame(columns=required_columns)
    else:
        df = pd.DataFrame(columns=required_columns)

    if not ((df["Name"] == name) & (df["Date"] == today_date)).any():
        new_row = pd.DataFrame([[name, today_date]], columns=required_columns)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(file_name, index=False)
        print(f"Attendance Marked: {name}")
    else:
        print(f"{name} already marked today.")

# ---------------------- MAIN APP ----------------------
class FaceRecognitionApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Face Recognition Attendance System (FAST DNN)")
        self.window.geometry("950x800")
        self.window.configure(bg="#f0f0f0")

        self.video_label = Label(window)
        self.video_label.pack()

        self.button_frame = ttk.Frame(window, padding=10)
        self.button_frame.pack()

        self.add_image_button = ttk.Button(self.button_frame, text="Add New Image", command=self.add_image)
        self.add_image_button.grid(row=0, column=0, padx=5)

        self.start_button = ttk.Button(self.button_frame, text="Start Recognition", command=self.start_recognition)
        self.start_button.grid(row=0, column=1, padx=5)

        self.stop_button = ttk.Button(self.button_frame, text="Stop Recognition", command=self.stop_recognition, state=DISABLED)
        self.stop_button.grid(row=0, column=2, padx=5)

        self.present_label = Label(window, text="Present Students:", font=("Arial", 11, "bold"))
        self.present_label.pack(pady=5)

        self.present_listbox = Listbox(window, width=60, height=8)
        self.present_listbox.pack(pady=5)

        self.absent_label = Label(window, text="Absent Students:", font=("Arial", 11, "bold"))
        self.absent_label.pack(pady=5)

        self.absent_listbox = Listbox(window, width=60, height=8)
        self.absent_listbox.pack(pady=5)

        self.status_var = StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(window, textvariable=self.status_var, relief=SUNKEN, anchor=W)
        self.status_bar.pack(side=BOTTOM, fill=X)

        # Webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Webcam not accessible.")
            exit(1)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.current_frame = None
        self.latest_faces = []
        self.present_students = set()

        self.recognition_running = False

        self.update_video_feed()

    # ---------------------- LIVE VIDEO FEED ----------------------
    def update_video_feed(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            self.current_frame = frame.copy()

            # Draw latest recognition boxes
            for (x1, y1, x2, y2, label, color) in self.latest_faces:
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            imgtk = ImageTk.PhotoImage(image=img)

            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.window.after(10, self.update_video_feed)

    # ---------------------- ADD IMAGE ----------------------
    def add_image(self):
        img_name = simpledialog.askstring("Input", "Enter Roll Number / Name:")
        if img_name:
            img_name = img_name.upper()
            img_path = os.path.join(IMAGE_DIR, img_name + ".jpg")

            if self.current_frame is not None:
                cv2.imwrite(img_path, self.current_frame)
                messagebox.showinfo("Success", f"Image saved as {img_name}.jpg")
            else:
                messagebox.showerror("Error", "No frame captured.")

    # ---------------------- START RECOGNITION ----------------------
    def start_recognition(self):
        self.recognition_running = True
        self.present_students = set()
        self.latest_faces = []

        self.present_listbox.delete(0, END)
        self.absent_listbox.delete(0, END)

        self.start_button.config(state=DISABLED)
        self.stop_button.config(state=NORMAL)

        self.status_var.set("Recognition Started...")

        def recognition_loop():
            while self.recognition_running:
                if self.current_frame is None:
                    continue

                frame = self.current_frame.copy()
                h, w = frame.shape[:2]

                blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300),
                                             (104.0, 177.0, 123.0))
                net.setInput(blob)
                detections = net.forward()

                temp_faces = []

                for i in range(detections.shape[2]):
                    confidence = detections[0, 0, i, 2]

                    if confidence > 0.6:
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (x1, y1, x2, y2) = box.astype("int")

                        # Add padding
                        padding = 25
                        x1 = max(0, x1 - padding)
                        y1 = max(0, y1 - padding)
                        x2 = min(w, x2 + padding)
                        y2 = min(h, y2 + padding)

                        face_img = frame[y1:y2, x1:x2]
                        if face_img.size == 0:
                            continue

                        rgb_face = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
                        fh, fw = rgb_face.shape[:2]

                        face_location_crop = [(0, fw, fh, 0)]
                        encodings = face_recognition.face_encodings(rgb_face, face_location_crop)

                        if encodings:
                            encodeFace = encodings[0]

                            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                            bestMatchIndex = np.argmin(faceDis)

                            if matches[bestMatchIndex] and faceDis[bestMatchIndex] < 0.5:
                                name = classNames[bestMatchIndex]

                                if name not in self.present_students:
                                    winsound.Beep(1000, 200)

                                self.present_students.add(name)
                                markAttendance(name)

                                temp_faces.append((x1, y1, x2, y2, name, (0, 255, 0)))
                            else:
                                temp_faces.append((x1, y1, x2, y2, "UNKNOWN", (0, 0, 255)))
                        else:
                            temp_faces.append((x1, y1, x2, y2, "UNKNOWN", (0, 0, 255)))

                self.latest_faces = temp_faces

                # Update present listbox
                self.present_listbox.delete(0, END)
                for s in sorted(self.present_students):
                    self.present_listbox.insert(END, s)

                time.sleep(0.2)

        threading.Thread(target=recognition_loop, daemon=True).start()

    # ---------------------- STOP RECOGNITION ----------------------
    def stop_recognition(self):
        self.recognition_running = False
        self.latest_faces = []

        self.start_button.config(state=NORMAL)
        self.stop_button.config(state=DISABLED)

        self.status_var.set("Recognition Stopped.")

        absent_students = all_roll_numbers - self.present_students

        self.absent_listbox.delete(0, END)
        for roll_no in sorted(absent_students):
            self.absent_listbox.insert(END, roll_no)

    def on_closing(self):
        self.recognition_running = False
        self.cap.release()
        self.window.destroy()

# ---------------------- RUN APP ----------------------
if __name__ == "__main__":
    root = Tk()
    app = FaceRecognitionApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
