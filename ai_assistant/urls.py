from django.urls import path
from .views import ChatAPIView,HealthCheckAPIView,SearchAPIView,DocumentStatsAPIView

urlpatterns = [
    path('search/', SearchAPIView.as_view(), name='search'),
    path('chat/', ChatAPIView.as_view(), name='chat'),
    path('health/', HealthCheckAPIView.as_view(), name='health'),
    path('stats/', DocumentStatsAPIView.as_view(), name='document_stats'),
]
