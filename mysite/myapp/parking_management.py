import json
import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator
from django.utils import timezone
import traceback

class ParkingManagement:
    """Zarządzanie miejscami parkingowymi za pomocą YOLO, wyjście do weba."""

    def __init__(self, model, json_file, occupied_region_color=(0,0,255), available_region_color=(0,255,0)):
        self.model = YOLO(model)

        with open(json_file) as f:
            self.json_data = json.load(f)

        self.occ = occupied_region_color
        self.arc = available_region_color
        self.pr_info = {"Zajete": 0, "Wolne": 0}

        # Klasy pojazdów do wykrywania (COCO indices: 2=car, 3=motorcycle, 5=bus, 7=truck, 8=boat)
        self.vehicle_classes = [2, 3, 5, 7, 8]

        # Optymalizacja - YOLO co 125 klatek
        self.frame_counter = 0
        self.process_every_n = 125
        self.last_boxes = []           # ostatnie wykrycia
        self.last_classes = []

      
        # sprawdzane jest czy miejsca mają zdefiniowane "spot_number", jeśli nie, to używa się idx jako numeru miejsca.
        self.spot_map = {}
        for idx, region in enumerate(self.json_data, start=1):
            if isinstance(region, dict):
                spot_num = region.get("spot_number", idx) 
            else: 
                spot_num = idx 
            self.spot_map[idx] = int(spot_num) 

        # stan miejsc parkingowych (klucz = rzeczywisty numer miejsca, wartość = zajęte/wolne)
        self.occupancy_state = {spot_num: False for spot_num in self.spot_map.values()}

        # debounce: minimalny odstęp (w sekundach) między kolejnymi zapisami dla jednego miejsca
        self.debounce_seconds = 5

    def process_data(self, frame):
        """Przetwarzanie jednej klatki z redukowaną częstotliwością YOLO."""
    
        self.frame_counter += 1
    
        # YOLO działa co 125 klatek
        if self.frame_counter % self.process_every_n == 0:
            print(f"\n{'='*60}")
            print(f"YOLO RUN - klatka {self.frame_counter}")
            print(f"Rozmiar klatki: {frame.shape}")
            
            results = self.model.predict(
                frame, 
                conf=0.25,
                iou=0.7,
                classes=self.vehicle_classes,  # filtrowanie tylko wybranych obiektów w modelu
                verbose=False
            )
            
            # log każdego wykrycia
            if results[0].boxes is not None and len(results[0].boxes) > 0:
                print(f"Wykryto {len(results[0].boxes)} obiektów")
                
                self.last_boxes = results[0].boxes.xyxy.cpu().tolist()
                self.last_classes = results[0].boxes.cls.cpu().tolist()
                confs = results[0].boxes.conf.cpu().tolist()
                
                for i, (box, cls, conf) in enumerate(zip(self.last_boxes, self.last_classes, confs)):
                    class_name = self.model.names[int(cls)]
                    print(f"  #{i}: {class_name} (klasa {int(cls)}) - pewność: {conf:.2%}")
                    print(f"       bbox: x1={box[0]:.0f}, y1={box[1]:.0f}, x2={box[2]:.0f}, y2={box[3]:.0f}")
            else:
                print("BRAK WYKRYĆ!")
                self.last_boxes = []
                self.last_classes = []
            
            print(f"{'='*60}\n")
            
        # inne klatki korzystają z poprzednich wyników
        boxes = self.last_boxes
    
        empty_slots = len(self.json_data)
        filled_slots = 0

        # numerowanie miejsca zaczynając od 1
        for idx, region in enumerate(self.json_data, start=1):
            pts_array = np.array(region["points"], dtype=np.int32).reshape((-1,1,2))
            occupied = False
    
            for box in boxes:
                xc = int((box[0]+box[2])/2)
                yc = int((box[1]+box[3])/2)
                
                # sprawdzanie, czy środek wykrytego obiektu znajduje się wewnątrz regionu miejsca parkingowego
                if cv2.pointPolygonTest(pts_array, (xc, yc), False) >= 0:
                    occupied = True
                    break
    
            color = self.occ if occupied else self.arc
            cv2.polylines(frame, [pts_array], isClosed=True, color=color, thickness=2)
    
            if occupied:
                filled_slots += 1
                empty_slots -= 1

            # ZAPIS DO BAZY: tylko przy przejściu z wolnego na zajęte
            spot_number = self.spot_map.get(idx, idx)  # używanie stabilnego numeru miejsca
            prev_state = self.occupancy_state.get(spot_number, False)
            if occupied and not prev_state:
                try:
                    # Lazy import - unika błędu AppRegistryNotReady podczas ładowania aplikacji.
                    # Django wymaga pełnej inicjalizacji rejestru aplikacji przed dostępem do modeli.
                    # Import na poziomie modułu (górnej części pliku) spowodowałby cykliczną zależność,
                    # ponieważ ten moduł jest ładowany przed zakończeniem setupu Django.
                    # Importując modele w momencie rzeczywistego użycia (runtime), jest pewność,
                    # że Django już skończył inicjalizację i modele są dostępne.
                    from django.apps import apps
                    ParkingSpot = apps.get_model('myapp', 'ParkingSpot')
                    ParkingOccupation = apps.get_model('myapp', 'ParkingOccupation')

                    # tworzenie/znajdowanie obiektu miejsca
                    spot, _ = ParkingSpot.objects.get_or_create(spot_number=spot_number)

                    # debounce: sprawdzanie ostatniego zajęcia i pominięcie gdy za świeże
                    last = ParkingOccupation.objects.filter(parking_spot=spot).order_by('-occupied_at').first()
                    if last is None or (timezone.now() - last.occupied_at).total_seconds() > self.debounce_seconds:
                        ParkingOccupation.objects.create(parking_spot=spot)
                    else:
                        print(f"Pominięcie duplikatu zapisu w bazie dla miejsca {spot_number}; ostatni wpis {timezone.localtime(last.occupied_at)}")


                except Exception as e:
                    print(f"Zapis w bazie danych nie powiódł się dla miejsca {spot_number}: {e}")
                    
            # aktualizacja stanu (klucz = rzeczywisty numer miejsca)
            self.occupancy_state[spot_number] = occupied

            # Obliczanie środka regionu do podpisu numerem (z bezpiecznym fallbackem)
            M = cv2.moments(pts_array)
            if M.get('m00', 0) != 0:
                cX = int(M['m10'] / M['m00'])
                cY = int(M['m01'] / M['m00'])
            else:
                pts_flat = pts_array.reshape(-1, 2)
                cX = int(np.mean(pts_flat[:, 0]))
                cY = int(np.mean(pts_flat[:, 1]))

            # przygotowanie tekstu, pozycjonowanie, centrowane
            label = str(idx)
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            thickness_fg = 2
            thickness_bg = 4
            (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, thickness_fg)
            text_pos = (cX - text_w // 2, cY + text_h // 2)

            # najpierw czarny obrys (lepszy kontrast), potem biały tekst
            cv2.putText(frame, label, text_pos, font, font_scale, (0, 0, 0), thickness_bg, cv2.LINE_AA)
            cv2.putText(frame, label, text_pos, font, font_scale, (255, 255, 255), thickness_fg, cv2.LINE_AA)
    
        self.pr_info["Zajete"] = filled_slots
        self.pr_info["Wolne"] = empty_slots
    
        # tekst - obrys i kolorowanie dla lepszej widoczności
        y0, dy = 30, 30
        for i, (k, v) in enumerate(self.pr_info.items()):
            text = f"{k}: {v}"
            pos = (10, y0 + i*dy)
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1
            thickness_bg = 4  # grubszy czarny obrys
            thickness_fg = 2  # kolorowy tekst na wierzchu

            # wybór koloru w zależności od klucza (wolne zielone, zajete czerwone)
            key_lower = k.lower()
            if key_lower.startswith("wol") or key_lower.startswith("w"):
                color = (0, 255, 0)      # jasna zieleń
            elif key_lower.startswith("zaj") or key_lower.startswith("z"):
                color = (0, 0, 255)      # czerwony
            else:
                color = (0, 255, 255)    # żółty fallback

            # najpierw czarny obrys, potem kolorowy tekst - lepszy kontrast
            cv2.putText(frame, text, pos, font, font_scale, (0, 0, 0), thickness_bg, cv2.LINE_AA)
            cv2.putText(frame, text, pos, font, font_scale, color, thickness_fg, cv2.LINE_AA)
    
        return frame