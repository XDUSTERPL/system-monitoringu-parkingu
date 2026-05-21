# System monitoringu parkingu

Projekt inżynierski polegający na stworzeniu systemu monitoringu parkingu wykorzystującego analizę obrazu w czasie rzeczywistym.

Aplikacja pobiera strumień RTSP z kamery IP działającej w prywatnej sieci 5G, analizuje zajętość miejsc parkingowych przy użyciu modelu YOLO i prezentuje wyniki w aplikacji webowej.

## Funkcjonalności

- pobieranie obrazu z kamery IP
- przetwarzanie obrazu oraz analiza zajętości miejsc parkingowych w czasie rzeczywistym z wykorzystaniem OpenCV i modelu YOLO
- zapis i odczyt danych statystycznych z bazy PostgreSQL
- podgląd przetworzonego strumienia RTSP oraz przegląd statystyk wykorzystania parkingu dostępnych dla zalogowanych użytkowników

## Technologie

- JavaScript, React
- Python, Django, OpenCV, YOLO
- PostgreSQL

## Architektura

Frontend odpowiada za prezentację wyników analizy oraz interakcję użytkownika z systemem.
Backend odpowiada za przetwarzanie obrazu, komunikację z kamerą IP oraz obsługę danych i logiki aplikacji.
