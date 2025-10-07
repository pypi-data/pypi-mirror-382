import cv2, serial, time, random

def connect_serial(port="COM4"):
    try:
        esp = serial.Serial(port, 115200, timeout=1)
        time.sleep(2)
        print("✅ ESP32 Connected!")
        return esp
    except Exception as e:
        print("⚠️ ESP32 not connected:", e)
        return None

def start_camera():
    return cv2.VideoCapture(0)

def read_frame(video):
    return video.read()

def simulate_face_detection(known_faces):
    if not known_faces:
        return False
    return random.choice([True, False])

def open_door(esp32, door_open):
    if not door_open:
        if esp32:
            esp32.write(b"O")
        print("✅ Door Open (Known Face Only)")
    return "DOOR OPEN", True

def close_door(esp32, door_open):
    if door_open:
        if esp32:
            esp32.write(b"C")
        print("❌ Door Closed")
    return "DOOR CLOSED", False

def draw_status(frame, status):
    h, w, _ = frame.shape
    box_height = 60
    y1, y2 = h - box_height, h
    half_w = w // 2
    cv2.rectangle(frame, (0, y1), (half_w, y2), (255, 0, 0), -1)
    cv2.rectangle(frame, (half_w, y1), (w, y2), (0, 255, 0), -1)
    cv2.line(frame, (half_w, y1), (half_w, y2), (255, 255, 255), 2)
    text_size = cv2.getTextSize(status, cv2.FONT_HERSHEY_DUPLEX, 1, 2)[0]
    text_x = (w - text_size[0]) // 2
    text_y = h - (box_height // 2) + (text_size[1] // 2)
    cv2.putText(frame, status, (text_x, text_y),
                cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

def show_instruction(frame, text):
    cv2.putText(frame, text, (20, 40),
                cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)

def display_frame(window, frame):
    cv2.imshow(window, frame)
    return cv2.waitKey(1) & 0xFF

def cleanup(video):
    video.release()
    cv2.destroyAllWindows()
