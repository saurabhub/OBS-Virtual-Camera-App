import obspython as obs
import cv2
import numpy as np
import socket
import threading
import struct
import time

# Global variables
is_streaming = False
server_ip = "192.168.1.100"  # Default IP
server_port = 5005
udp_socket = None

def get_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "server_ip", "Android Device IP", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(props, "server_port", "Port", 1024, 65535, 1)
    obs.obs_properties_add_button(props, "start_button", "Start/Stop Streaming", toggle_streaming)
    return props

def get_defaults(settings):
    obs.obs_data_set_default_string(settings, "server_ip", server_ip)
    obs.obs_data_set_default_int(settings, "server_port", server_port)

def update(settings):
    global server_ip, server_port
    server_ip = obs.obs_data_get_string(settings, "server_ip")
    server_port = obs.obs_data_get_int(settings, "server_port")

def toggle_streaming(props, prop):
    global is_streaming, udp_socket
    is_streaming = not is_streaming
    
    if is_streaming:
        try:
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Add video capture callback
            video_info = obs.obs_video_info()
            obs.obs_add_raw_video_callback(video_info, video_callback, None)
            print(f"Started streaming to {server_ip}:{server_port}")
        except Exception as e:
            print(f"Error starting stream: {e}")
            is_streaming = False
    else:
        obs.obs_remove_raw_video_callback(video_callback, None)
        if udp_socket:
            udp_socket.close()
            udp_socket = None
        print("Stopped streaming")
    return True

def video_callback(param, video_data):
    if not is_streaming or not udp_socket:
        return
        
    try:
        # Extract raw frame data (assuming NV12 or RGBA depending on OBS settings)
        # For simplicity, getting the raw buffer. In a real scenario, proper format conversion 
        # is needed based on video_data.format
        
        width = obs.obs_video_info().base_width
        height = obs.obs_video_info().base_height
        
        # Convert raw data to numpy array
        # Note: This is simplified. Actual OBS raw callback needs proper stride handling
        raw_data = bytes(video_data.data[0]) 
        frame = np.frombuffer(raw_data, dtype=np.uint8).reshape((height, width, 4))
        
        # Convert RGBA to BGR for OpenCV
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
        
        # Resize to 720p to reduce bandwidth
        frame_resized = cv2.resize(frame_bgr, (1280, 720))
        
        # Encode as JPEG (Quality 70 for low latency/good compression)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
        _, buffer = cv2.imencode('.jpg', frame_resized, encode_param)
        
        # UDP Datagram max size is 65507 bytes.
        # For frames larger than UDP limit, we chunk them.
        chunk_size = 60000
        byte_data = buffer.tobytes()
        total_chunks = len(byte_data) // chunk_size + 1
        
        for i in range(total_chunks):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, len(byte_data))
            
            # Simple header: [Frame ID (4 bytes)] [Total Chunks (1 byte)] [Chunk ID (1 byte)] [Payload]
            # Since this is a basic example, we just send to port directly.
            chunk = byte_data[start:end]
            udp_socket.sendto(chunk, (server_ip, server_port))
            
    except Exception as e:
        print(f"Error processing frame: {e}")

def script_description():
    return "Sends OBS Program Output to Android Virtual Camera App via UDP.\nConfigure the Android device's IP address."
