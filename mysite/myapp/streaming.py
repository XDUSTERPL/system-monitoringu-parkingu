import os
import cv2
import time
import threading
from .parking_management import ParkingManagement

#  ŚCIEŻKI DO PLIKÓW
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "yolo11m.pt")
JSON_PATH = os.path.join(BASE_DIR, "bounding_boxes.json")

# Inicjalizacja klasy zarządzania parkingiem (YOLO + bounding boxy)
parking_manager = ParkingManagement(
    model=MODEL_PATH,
    json_file=JSON_PATH
)

latest_frame = None # ostatnia przetworzona klatka
stop_flag = False # flaga do zatrzymania pętli (gdyby była potrzebna)

#  WĄTEK PRZETWARZAJĄCY YOLO W TLE
def processing_loop():
    """Główna pętla odtwarzania RTSP stream + YOLO."""

    global latest_frame, stop_flag

    # Otwieranie strumienia RTSP
    cap = cv2.VideoCapture("rtsp://pans:Pans2025@192.168.55.13/axis-media/media.amp")
    if not cap.isOpened():
        raise RuntimeError("Nie udało się połączyć ze strumieniem RTSP!")

    # Sprawdzanie rozdzielczości strumienia
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"RTSP rozdzielczość: {width}x{height}")

    # Jeśli rozdzielczość < 640px
    if width < 640:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


    # Bufor na 1 klatkę (zmniejsza opóźnienie)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)


    #GŁÓWNA PĘTLA RTSP + YOLO
    while not stop_flag:
        ret, frame = cap.read() # Pobieranie najnowszej klatki ze strumienia

        # Jeśli stracono połączenie, próba ponownego połączenia
        if not ret:
            print("Utracono połączenie RTSP, próba ponownego połączenia...")
            cap.release()
            time.sleep(2)  # Czekanie przed ponownym połączeniem
            cap = cv2.VideoCapture("rtsp://pans:Pans2025@192.168.55.13/axis-media/media.amp")
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            continue

        # YOLO - działa co 30 klatek
        frame = parking_manager.process_data(frame)

        latest_frame = frame # zapisanie ostatniej przetworzonej klatki

    cap.release()

#  URUCHAMIANIE WĄTKU YOLO (Tylko raz)
def start_processing_thread():
    """
    Start osobnego wątku, który stale generuje klatki.
    Dzięki temu frontend jest płynny.
    """
    thread = threading.Thread(target=processing_loop, daemon=True)
    thread.start()


#  GENERATOR STREAMU MJPEG
def gen_frames():
    """Funkcja działa jak „podaj ostatnią gotową klatkę”.
    NIE ZAWIERA żadnego spowolnienia odtwarzania.
    Opóźnienie jest tylko w wątku YOLO."""
    global latest_frame

    while True:
        # Jeśli YOLO jeszcze nie wygenerował pierwszej klatki
        if latest_frame is None:
            time.sleep(0.01)
            continue

        # Kodowanie aktualnej klatki do JPEG
        ret, buffer = cv2.imencode('.jpg', latest_frame)
        frame_bytes = buffer.tobytes()

        # Format MJPEG wymagany przez HTML <img src="...">
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        # Krótka pauza - stream musi być szybki, bo to powoduje opóźnienie.
        time.sleep(0.01)