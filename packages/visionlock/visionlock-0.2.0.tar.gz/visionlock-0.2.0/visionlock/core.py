import cv2
import face_recognition
import serial
import time

def run_visionlock(port="COM4"):
    # ------------------- ESP32 Serial Setup -------------------
    esp32 = serial.Serial(port, 115200, timeout=1)
    time.sleep(2)
    print("✅ ESP32 Connected!")

    # ------------------- Storage Setup -------------------
    known_encodings, known_names = [], []
    print("⚠️ Starting with a fresh face database.")

    # ------------------- Timer & Door State -------------------
    last_seen_time = 0
    hold_time = 2  # seconds needed before opening
    door_open = False
    buzzer_triggered = False  # To beep only once per unknown
    door_status = "WAITING..."  # text label

    # ------------------- Start Webcam -------------------
    video = cv2.VideoCapture(0)

    while True:
        ret, frame = video.read()
        if not ret:
            break

        # Resize for speed
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        recognized_face = False
        unknown_face = False

        # Process detected faces
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Scale back to original size
            top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4

            # Compare
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding) if known_encodings else []

            name = "Unknown"
            confidence = 0.0

            if len(face_distances) > 0:
                best_match_index = face_distances.argmin()
                confidence = (1 - face_distances[best_match_index]) * 100
                if matches[best_match_index]:
                    name = known_names[best_match_index]

            # Decision
            if name != "Unknown" and confidence > 70:
                recognized_face = True
            else:
                unknown_face = True

            # Draw Face Box
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, f"{name} ({confidence:.2f}%)", (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # ------------------- Door + Buzzer Control -------------------
        current_time = time.time()

        if recognized_face and not unknown_face:
            buzzer_triggered = False
            if last_seen_time == 0:
                last_seen_time = current_time
            elif (current_time - last_seen_time) >= hold_time and not door_open:
                esp32.write(b"O")
                print("✅ Door Open (Known Face Only)")
                door_open = True
                door_status = "DOOR OPEN "
            elif door_open:
                last_seen_time = current_time
        else:
            last_seen_time = 0
            if door_open:
                esp32.write(b"C")
                print("❌ Door Closed")
                door_open = False
                door_status = "DOOR CLOSED "

            if unknown_face and known_encodings and not buzzer_triggered:
                esp32.write(b"B")
                print("🚨 Buzzer Beep (Unknown Face Detected)")
                buzzer_triggered = True
                door_status = "UNKNOWN FACE "

        # ------------------- Draw Door Status Box -------------------
        h, w, _ = frame.shape
        box_height = 60
        y1, y2 = h - box_height, h
        half_w = w // 2

        cv2.rectangle(frame, (0, y1), (half_w, y2), (255, 0, 0), -1)
        cv2.rectangle(frame, (half_w, y1), (w, y2), (0, 255, 0), -1)
        cv2.line(frame, (half_w, y1), (half_w, y2), (255, 255, 255), 2)

        text_size = cv2.getTextSize(door_status, cv2.FONT_HERSHEY_DUPLEX, 1, 2)[0]
        text_x = (w - text_size[0]) // 2
        text_y = h - (box_height // 2) + (text_size[1] // 2)
        cv2.putText(frame, door_status, (text_x, text_y),
                    cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("VisionLock Security System", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("s") and len(face_encodings) > 0:
            person_name = input("Enter name for this face: ")
            known_encodings.append(face_encodings[0])
            known_names.append(person_name)
            print(f"✅ Saved face for {person_name}")
            door_status = f"FACE SAVED: {person_name}"
        if key == 27:
            break

    video.release()
    cv2.destroyAllWindows()
    esp32.close()
