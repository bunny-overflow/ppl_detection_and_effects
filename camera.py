import cv2
import numpy as np
from datetime import datetime
from PIL import Image, ImageTk
from ultralytics import YOLO

class Camera:
    def __init__(self, label_image, var_filter, strength, isdone, model_path="yolov8n.pt"):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Cannot open camera")
        self.label_image = label_image
        self.var_filter = var_filter
        self.strength = strength
        self.isdone = isdone
        self.model = YOLO(model_path)
        self.camera_running = False
        self.ss_flag = False
        self.frame = None

    def apply_filter(self, frame):
        filter_name = self.var_filter.get()
        strength_val = self.strength.get()

        if filter_name == "Grayscale":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blended = cv2.addWeighted(frame, (100 - strength_val) / 100,
                                      cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR), strength_val / 100, 0)
            return blended

        elif filter_name == "Negative":
            inv = cv2.bitwise_not(frame)
            return cv2.addWeighted(frame, (100 - strength_val) / 100, inv, strength_val / 100, 0)

        elif filter_name == "Gaussian Blur":
            ksize = abs(strength_val)
            if ksize % 2 == 0:
                ksize += 1
            return cv2.GaussianBlur(frame, (ksize, ksize), 0)

        elif filter_name == "Edge Detection":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return cv2.Canny(gray, strength_val, strength_val * 2)

        elif filter_name == "Binary":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, strength_val, 255, cv2.THRESH_BINARY)
            return binary

        elif filter_name == "Sepia":
            img = frame.astype(float)
            sepia_filter = np.array([[0.272, 0.534, 0.131],
                                     [0.349, 0.686, 0.168],
                                     [0.393, 0.769, 0.189]])
            sepia_img = cv2.transform(img, sepia_filter)
            sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
            strength_val = strength_val / 100.0
            return cv2.addWeighted(frame, 1 - strength_val, sepia_img, strength_val, 0)

        elif filter_name == "Glitch":
            b, g, r = cv2.split(frame)
            rows, cols = b.shape
            stren = int(strength_val)
            M_shift_r = np.float32([[1, 0, stren], [0, 1, 0]])
            M_shift_b = np.float32([[1, 0, -stren], [0, 1, 0]])
            r_shifted = cv2.warpAffine(r, M_shift_r, (cols, rows))
            b_shifted = cv2.warpAffine(b, M_shift_b, (cols, rows))
            return cv2.merge((b_shifted, g, r_shifted))

        else:
            return frame

    def update_frame(self, root, fps_var):
        if not self.camera_running:
            return
        ret, frame = self.cap.read()
        if not ret:
            return

        if self.isdone.get():
            results = self.model.predict(source=frame, classes=[0], show=False)
            frame = results[0].plot()
            boxes = results[0].boxes
            detections = [box for box in boxes if box.conf.item() >= 0.5]
            cv2.putText(frame, f"Detections amount: {len(detections)}", (30, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3, cv2.LINE_AA)

        frame = self.apply_filter(frame)

        if self.ss_flag:
            self.ss_flag = False
            now = datetime.now()
            filename = now.strftime("%Y-%m-%d_%H-%M-%S") + ".png"
            cv2.imwrite(filename, frame)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        self.label_image.imgtk = imgtk
        self.label_image.configure(image=imgtk)

        delay = int(1000 / fps_var.get())
        root.after(delay, lambda: self.update_frame(root, fps_var))

    def start(self, root, fps_var):
        if not self.camera_running:
            self.camera_running = True
            self.update_frame(root, fps_var)

    def stop(self):
        self.camera_running = False

    def screenshot(self):
        self.ss_flag = True

    def release(self):
        self.cap.release()

    def set_resolution(self, width, height):
        self.stop()
        self.cap.release()
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
