# FACE-LOG
Facial Recognition-Based Student Attendance System.


# FaceLog - AI Face Recognition Attendance System

FaceLog is a facial recognition-based attendance system developed using Python, OpenCV, face_recognition, Tkinter, and Pandas.

## Features

- Real-time face recognition
- Automatic attendance marking
- One attendance per person per day
- CSV/Excel attendance records
- Tkinter GUI
- Live webcam detection
- Unknown face detection

---

# Requirements

## Operating System

- Windows 10 or Windows 11 (64-bit)

---

## Software Required

Install the following before running the project.

### 1. Python

**Recommended Version**

Python **3.11.x (64-bit)**

⚠️ Do NOT use Python 3.14 or newer.

The `face_recognition` library depends on `dlib`, which currently has installation issues on Python 3.14.

Download:

https://www.python.org/downloads/release/python-3119/

During installation:

- ✅ Add Python to PATH
- ✅ Install for all users (Optional)

---

### 2. Git

Download Git:

https://git-scm.com/downloads

Verify:

```bash
git --version
```

---

### 3. Visual Studio Community / Build Tools

Download:

https://visualstudio.microsoft.com/downloads/

During installation select:

✅ Desktop development with C++

Required Components:

- MSVC v143 C++ Build Tools
- Windows 10/11 SDK
- C++ CMake tools for Windows

Restart your computer after installation.

---

# Clone Repository

```bash
git clone https://github.com/USERNAME/REPOSITORY.git
```

Go into project folder

```bash
cd Face_recognition_project
```

---

# Create Virtual Environment

Windows PowerShell

```powershell
python -m venv .venv
```

Activate Virtual Environment

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

```powershell
.\.venv\Scripts\Activate.ps1
```

You should now see

```text
(.venv)
```

---

# Upgrade pip

```bash
python -m pip install --upgrade pip
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

or manually

```bash
pip install

opencv-python
numpy
pandas
Pillow
openpyxl
face-recognition
```

---

# Verify Installation

Run

```bash
python
```

Then

```python
import cv2
import face_recognition
import pandas
import PIL
```

No errors means installation is successful.

Exit

```python
exit()
```

---

# Project Structure

```
Face_recognition_project
│
├── Images/
├── Attendance/
├── models/
├── MAIN PROJECT.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Running the Project

Activate virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

Run

```bash
python "MAIN PROJECT.py"
```

---
# Developed By

Aryaan Shaikh

KJ College of Engineering & Management Research

Bachelor of Engineering

Computer Engineering

---
