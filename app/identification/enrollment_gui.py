"""
Face Enrollment GUI — Simple Tkinter Window
============================================
Captures face samples and enrolls a person into the database.
"""
import tkinter as tk
from tkinter import messagebox, simpledialog
import cv2
from PIL import Image, ImageTk
import threading
import time


class EnrollmentGUI:
    """
    Simple GUI for enrolling a new person's face.
    Shows live camera feed and guides through capture.
    """

    def __init__(self, face_recognizer, person_db, camera_index=0):
        self.recognizer = face_recognizer
        self.db = person_db
        self.camera_index = camera_index
        self.cap = None
        self.captured_faces = []  # list of face crops
        self.required_samples = 3
        self.running = True

    def start(self):
        """Open camera and show enrollment window. Returns person_id or None."""
        # Open camera
        for idx in [self.camera_index, 0, 1, 2]:
            self.cap = cv2.VideoCapture(idx)
            if self.cap.isOpened():
                self.camera_index = idx
                break

        if not self.cap or not self.cap.isOpened():
            messagebox.showerror("Error", "No camera available for enrollment.")
            return None

        # Get person name
        root = tk.Tk()
        root.withdraw()  # hide main window
        name = simpledialog.askstring(
            "Enroll Person",
            "Enter the person's full name:",
            parent=root
        )
        root.destroy()

        if not name or not name.strip():
            if self.cap:
                self.cap.release()
            return None

        name = name.strip()

        if self.db.person_exists(name):
            messagebox.showwarning("Already Enrolled", f"'{name}' is already enrolled.")
            self.cap.release()
            return None

        # Build GUI
        self.window = tk.Tk()
        self.window.title(f"Enrolling: {name}")
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        # Camera display
        self.camera_label = tk.Label(self.window)
        self.camera_label.pack(padx=10, pady=10)

        # Status
        self.status_label = tk.Label(
            self.window,
            text=f"Capturing {self.required_samples} face samples...\n"
                 f"Look at the camera. Captured: 0/{self.required_samples}",
            font=("Arial", 12),
            fg="blue",
        )
        self.status_label.pack(pady=5)

        # Capture button
        self.capture_btn = tk.Button(
            self.window, text="📸 Capture Face", font=("Arial", 14),
            bg="#4CAF50", fg="white", command=self._capture
        )
        self.capture_btn.pack(pady=10)

        self.window.geometry("500x500")
        self.window.resizable(False, False)

        # Start camera feed
        self._update_camera()

        self.window.mainloop()
        self.running = False

        if self.cap:
            self.cap.release()

        # If enough samples were captured, enroll
        if len(self.captured_faces) >= self.required_samples:
            embeddings = []
            for face in self.captured_faces:
                emb = self.recognizer.get_embedding(face)
                if emb is not None:
                    embeddings.append(emb)

            if len(embeddings) >= self.required_samples:
                try:
                    pid = self.db.enroll(name, embeddings)
                    messagebox.showinfo(
                        "✅ Enrollment Complete",
                        f"Successfully enrolled:\n\n"
                        f"  Name: {name}\n"
                        f"  ID: {pid}\n"
                        f"  Samples: {len(embeddings)}"
                    )
                    return pid
                except Exception as e:
                    messagebox.showerror("Error", f"Database error: {e}")
            else:
                messagebox.showerror(
                    "Error",
                    "Could not extract embeddings from captured faces. Please try again."
                )
        else:
            # Window closed without enough captures
            pass

        return None

    def _update_camera(self):
        """Refresh camera feed in the GUI."""
        if not self.running:
            return

        ret, frame = self.cap.read()
        if ret:
            # Mirror for selfie view
            frame = cv2.flip(frame, 1)

            # Detect faces and draw rectangle
            faces = self.recognizer.detect_faces(frame)
            for face in faces:
                x, y, w, h = face['bbox']
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Convert for tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((480, 360), Image.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)

        self.window.after(30, self._update_camera)

    def _capture(self):
        """Capture current face crop(s)."""
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        faces = self.recognizer.detect_faces(frame)

        if not faces:
            messagebox.showwarning("No Face", "No face detected. Please look at the camera.")
            return

        if len(faces) > 1:
            messagebox.showwarning(
                "Multiple Faces",
                "Only one face should be in the frame during enrollment."
            )
            return

        # Crop the face
        x, y, w, h = faces[0]['bbox']
        face_crop = frame[y:y+h, x:x+w]
        self.captured_faces.append(face_crop)

        n = len(self.captured_faces)
        self.status_label.configure(
            text=f"Captured: {n}/{self.required_samples}\n"
                 f"{'✅ Done! Close window to finish.' if n >= self.required_samples else 'Look at camera...'}"
        )

    def _on_close(self):
        self.running = False
        self.window.destroy()
