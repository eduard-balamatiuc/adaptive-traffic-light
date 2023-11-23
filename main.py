import streamlit as st
from PIL import Image
import time
import cv2
import threading
from ultralytics import YOLO

model = YOLO('yolov8n.pt')

# Initialize the session state
st.session_state.setdefault('light_color', None)

def load_and_crop_image(image_path):
    semafor = Image.open(image_path)
    return {
        'rosu': semafor.crop((75, 10, 425, 1014)),
        'galben': semafor.crop((450, 10, 850, 1014)),
        'verde': semafor.crop((850, 10, 1250, 1014)),
    }
semafor_images = load_and_crop_image('semafor.png')

# Create a placeholder for the traffic light image
image_placeholder = st.sidebar.empty()
ph = st.sidebar.empty()
camera_placeholder = st.empty()  # Placeholder for the camera feed

def update_light(color, duration):
    st.session_state['light_color'] = color
    time.sleep(duration)

def traffic_light_thread():
    print("Started thread")
    while True:
        print("Got here")
        update_light('rosu', 10)
        update_light('galben', 3)
        update_light('verde', 10)
        update_light('galben', 3)

# Camera feed loop
camera = cv2.VideoCapture(0)
# frame = cv2.imread('/media/eduard/New Volume1/self/my-personal-projects/adaptive-semafor/test.jpg')
time_to_pass = 15
time_to_stay = 20
results = None

def process_camera_feed():
    global time_to_pass, time_to_stay
    while True:
        time_to_pass = process_pass_phase(time_to_pass)
        time_to_stay = process_stay_phase(time_to_stay)
        
def process_pass_phase(time_to_pass):
    global results
    while time_to_pass > 0:
        display_camera_feed()
        time_to_pass = update_time_to_pass(time_to_pass)
        ph.text(f"Time to pass: {time_to_pass}")
        time.sleep(1)
    return 15
        
def process_stay_phase(time_to_stay):
    while time_to_stay > 0:
        ph.text(f"Time to stay: {time_to_stay}")
        time_to_stay = time_to_stay - 1
        time.sleep(1)
    return 20        

def display_camera_feed():
    global results
    ret, frame = camera.read()
    if ret:
        real = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = model.predict(real)
        res_plotted = results[0].plot()
        camera_placeholder.image(res_plotted, use_column_width=True)
    
def update_time_to_pass(time_to_pass):
    global results
    if time_to_pass <= 5 and 0 in list(results[0].boxes.cls):
        return 5
    return time_to_pass - 1

process_camera_feed()

