import cv2
import sys

video_path = sys.argv[1]

cap = cv2.VideoCapture(video_path)
length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
cap.set(cv2.CAP_PROP_POS_FRAMES, length // 2)

ret, frame = cap.read()
if not ret:
    print("CENTER")
    sys.exit(0)

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

faces = face_cascade.detectMultiScale(gray, 1.2, 5)

if len(faces) == 0:
    print("CENTER")
    sys.exit(0)

x, y, w, h = faces[0]
center_x = x + w // 2
print(center_x)
