# Face Recognition Project

This project contains a simple facial recognition GUI application using OpenCV, face_recognition, and MySQL.

Files:

- `facial_recognition.py` - Main application script.
- `requirements.txt` - Python dependencies.

Quick setup (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Notes:
- `dlib` can be difficult to build on Windows. Use a pre-built wheel or install via conda:
  - `conda create -n fr python=3.10` then `conda activate fr` and `conda install -c conda-forge dlib`.
- Configure your MySQL database and update connection credentials in `facial_recognition.py` before running.

How to push to GitHub:

1. Create a new repository on GitHub.
2. In PowerShell:

```powershell
cd "<path-to-project>"
git remote add origin https://github.com/<your-user>/<repo>.git
git branch -M main
git push -u origin main
```
