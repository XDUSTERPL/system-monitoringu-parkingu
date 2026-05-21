from django.urls import path
from . import views

urlpatterns = [
    path('test_auth/', views.test_auth, name='test_auth'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('get_parking_stats/', views.get_parking_stats, name='get_parking_stats'),
    
]
