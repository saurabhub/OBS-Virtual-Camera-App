import customtkinter as ctk
import cv2
import socket
import threading
import time
import numpy as np
from PIL import Image

# Set UI Theme and Colors
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class OBSSenderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("OBS to Android - UDP Sender")
        self.geometry("650x500")
        self.resizable(False, False)
        
        self.is_streaming = False
        self.udp_socket = None
        self.capture = None
        self.stream_thread = None
        
        self.build_ui()

    def build_ui(self):
        # Header title
        title_font = ctk.CTkFont(family="Roboto", size=26, weight="bold")
        self.title_label = ctk.CTkLabel(self, text="OBS Streamer Dashboard", font=title_font)
        self.title_label.pack(pady=(30, 20))
        
        # IP Address Frame
        self.frame_ip = ctk.CTkFrame(self, corner_radius=10)
        self.frame_ip.pack(pady=10, padx=40, fill="x")
        
        self.ip_label = ctk.CTkLabel(self.frame_ip, text="Android IP Address:")
        self.ip_label.pack(side="left", padx=20, pady=15)
        
        self.ip_entry = ctk.CTkEntry(self.frame_ip, width=220, placeholder_text="e.g. 192.168.1.100")
        self.ip_entry.insert(0, "192.168.1.100")
        self.ip_entry.pack(side="right", padx=20, pady=15)
        
        # Camera Index Frame
        self.frame_cam = ctk.CTkFrame(self, corner_radius=10)
        self.frame_cam.pack(pady=10, padx=40, fill="x")
        
        self.cam_label = ctk.CTkLabel(self.frame_cam, text="Camera Index (0=Webcam, 1=OBS Cam):")
        self.cam_label.pack(side="left", padx=20, pady=15)
        
        self.cam_entry = ctk.CTkEntry(self.frame_cam, width=100)
        self.cam_entry.insert(0, "1")
        self.cam_entry.pack(side="right", padx=20, pady=15)
        
        # Start/Stop Button
        btn_font = ctk.CTkFont(family="Roboto", size=18, weight="bold")
        self.start_btn = ctk.CTkButton(self, text="START STREAMING", fg_color="#2ECC71", hover_color="#27AE60", 
                                       text_color="white", font=btn_font, height=50, command=self.toggle_stream)
        self.start_btn.pack(pady=(30, 10), padx=40, fill="x")
        
        # Status Label
        status_font = ctk.CTkFont(family="Roboto", size=15)
        self.status_label = ctk.CTkLabel(self, text="Status: Ready to Stream", font=status_font, text_color="gray")
        self.status_label.pack(pady=10)

    def toggle_stream(self):
        if not self.is_streaming:
            self.start_stream()
        else:
            self.stop_stream()
            
    def start_stream(self):
        ip = self.ip_entry.get().strip()
        cam_idx_str = self.cam_entry.get().strip()
        cam_idx = int(cam_idx_str) if cam_idx_str.isdigit() else 0
        
        try:
            # Open video capture device
            self.capture = cv2.VideoCapture(cam_idx)
            if not self.capture.isOpened():
                self.status_label.configure(text=f"Status: Error opening camera index {cam_idx}", text_color="#E74C3C")
                return
                
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.is_streaming = True
            
            # Update UI
            self.start_btn.configure(text="STOP STREAMING", fg_color="#E74C3C", hover_color="#C0392B")
            self.status_label.configure(text=f"Status: Streaming Live to {ip}:5005...", text_color="#2ECC71")
            
            # Start Background Thread
            self.stream_thread = threading.Thread(target=self.stream_loop, args=(ip,), daemon=True)
            self.stream_thread.start()
            
        except Exception as e:
            self.status_label.configure(text=f"Status: Connection Error - {str(e)}", text_color="#E74C3C")
            self.stop_stream()

    def stop_stream(self):
        self.is_streaming = False
        if self.udp_socket:
            try:
                self.udp_socket.close()
            except: pass
            self.udp_socket = None
            
        if self.capture:
            self.capture.release()
            self.capture = None
            
        self.start_btn.configure(text="START STREAMING", fg_color="#2ECC71", hover_color="#27AE60")
        self.status_label.configure(text="Status: Stream Stopped", text_color="gray")

    def stream_loop(self, ip):
        port = 5005
        while self.is_streaming and self.capture and self.capture.isOpened():
            try:
                ret, frame = self.capture.read()
                if not ret:
                    continue
                    
                # Resize frame to 720p for fast transmission
                frame_resized = cv2.resize(frame, (1280, 720))
                
                # Compress to JPEG with medium quality (60) for low latency
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
                _, buffer = cv2.imencode('.jpg', frame_resized, encode_param)
                
                byte_data = buffer.tobytes()
                
                # UDP Packets max safe size is ~60,000 bytes. Chunk it if larger.
                chunk_size = 60000
                total_chunks = len(byte_data) // chunk_size + 1
                
                for i in range(total_chunks):
                    start = i * chunk_size
                    end = min((i + 1) * chunk_size, len(byte_data))
                    chunk = byte_data[start:end]
                    self.udp_socket.sendto(chunk, (ip, port))
                    
                # Add tiny sleep to prevent network flooding and handle frame rate (approx 30fps)
                time.sleep(0.03) 
                
            except Exception as e:
                # If window is closed or socket fails, break the loop quietly
                break

if __name__ == "__main__":
    app = OBSSenderApp()
    app.mainloop()
