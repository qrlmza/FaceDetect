from flask import Flask, render_template, Response
import cv2
import threading
import time
from discord_notifier import send_discord_notification

app = Flask(__name__)

username = 'username'
password = 'password'
camera_ip = 'adresse_ip'
stream = 'identifiant_flux' # par défaut cette veleur est souvent : stream1 / live

rtsp_url = f'rtsp://{username}:{password}@{camera_ip}/{stream}'

cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("Erreur: Impossible d'ouvrir le flux vidéo")
    exit()

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

frame = None
lock = threading.Lock()

def capture_frames():
    global frame
    while True:
        ret, new_frame = cap.read()
        if not ret:
            break
        with lock:
            frame = new_frame

thread = threading.Thread(target=capture_frames)
thread.daemon = True
thread.start()

def generate_frames():
    global frame
    while True:
        with lock:
            if frame is None:
                continue
            frame_resized = cv2.resize(frame, (640, 480))

        gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            cv2.rectangle(frame_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.png', frame_resized)
        frame_jpeg = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/png\r\n\r\n' + frame_jpeg + b'\r\n\r\n')

        if len(faces) > 0:
            send_discord_notification()

        time.sleep(0.5)  # Attente d'une seconde entre chaque frame pour ne pas surcharger le processeur

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
