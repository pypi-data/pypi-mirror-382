# VisionLock

VisionLock is a simple teaching-friendly Python library that helps students
understand how face-recognition and IoT (ESP32) systems work together.

### ✨ Features
- Connects to ESP32 via Serial
- Simulates door open/close logic
- Draws colorful status bars using OpenCV
- Simple enough for beginners to code in class

### 🚀 Example Demo
```python
import visionlock

esp = visionlock.connect_serial("COM4")
video = visionlock.start_camera()

while True:
    ret, frame = visionlock.read_frame(video)
    if not ret:
        break
    visionlock.show_instruction(frame, "Press 'S' to capture face")
    visionlock.draw_status(frame, "DOOR CLOSED")
    key = visionlock.display_frame("VisionLock Demo", frame)
    if key == 27:
        break

visionlock.cleanup(video)
