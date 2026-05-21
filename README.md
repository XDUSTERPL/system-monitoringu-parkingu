# System monitoringu parkingu

Projekt inżynierski polegający na stworzeniu systemu monitoringu parkingu wykorzystującego analizę obrazu w czasie rzeczywistym.

Aplikacja pobiera strumień RTSP z kamery IP działającej w prywatnej sieci 5G, analizuje zajętość miejsc parkingowych przy użyciu modelu YOLO i prezentuje wyniki w aplikacji webowej.

## Funkcjonalności

- pobieranie obrazu z kamery IP
- analiza zajętości miejsc parkingowych w czasie rzeczywistym z wykorzystaniem modelu YOLO
- prezentacja wyników w aplikacji webowej
- zapis i odczyt danych statystycznych z bazy PostgreSQL

## Technologie

- JavaScript, React
- Python, Django
- PostgreSQL
- YOLO

## Architektura

Frontend odpowiada za prezentację wyników analizy oraz interakcję użytkownika z systemem.
Backend realizuje przetwarzanie obrazu, komunikację z kamerą IP oraz obsługę danych.
