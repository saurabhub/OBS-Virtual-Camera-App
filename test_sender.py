import cv2
import numpy as np
import socket
import time

server_ip = "127.0.0.1"
server_port = 5005
try:
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Starting Mock Sender...")

    count = 0
    while count < 10:
        # Create a dummy image (720p)
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        # Give it some color that changes
        frame[:] = (0, count * 25, 255 - count * 25) 
        
        cv2.putText(frame, f"Test Frame {count}", (100, 360), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 8)
        
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
        _, buffer = cv2.imencode('.jpg', frame, encode_param)
        
        byte_data = buffer.tobytes()
        chunk_size = 60000
        total_chunks = len(byte_data) // chunk_size + 1
        
        for i in range(total_chunks):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, len(byte_data))
            chunk = byte_data[start:end]
            udp_socket.sendto(chunk, (server_ip, server_port))
        
        print(f"Sent Frame {count} ({len(byte_data)} bytes)")
        count += 1
        time.sleep(0.5)

    print("Sender finished.")
    udp_socket.close()
except Exception as e:
    print(f"Sender Error: {e}")
