from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'
    _thread_started = False  # Flaga zapobiegająca wielokrotnemu uruchomieniu

    def ready(self):
        """Wykonuje się po załadowaniu wszystkich ustawień Django"""
        from .streaming import start_processing_thread
        import os
        
        # Uruchomienie wątku tylko raz (zabezpieczenie przed autoreload Django)
        if not MyappConfig._thread_started and os.environ.get('RUN_MAIN') == 'true':
            MyappConfig._thread_started = True
            start_processing_thread()
            print("Wątek przetwarzania RTSP uruchomiony")