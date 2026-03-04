import socket
import cv2
import numpy as np
import time

PORT = 5005
try:
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("0.0.0.0", PORT))
    udp_socket.settimeout(5.0)

    print(f"UDP Receiver started on port {PORT}")

    received_frames = 0
    while received_frames < 5:
        try:
            data, addr = udp_socket.recvfrom(65535)
            print(f"Received chunk of size {len(data)} from {addr}")
            
            # Decode JPEG
            frame_array = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            
            if frame is not None:
                filename = f"received_frame_{received_frames}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Successfully decoded and saved {filename}")
                received_frames += 1
            else:
                print("Failed to decode frame from chunk.")
        except socket.timeout:
            print("Timeout waiting for packet.")
            break
        except Exception as e:
            print(f"Error: {e}")

    print("Receiver finished.")
    udp_socket.close()
except Exception as e:
    print(f"Receiver Setup Error: {e}")
