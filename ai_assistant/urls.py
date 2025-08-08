from django.urls import path
from .views import ChatAPIView,HealthCheckAPIView,SearchAPIView,DocumentStatsAPIView,ChatHistoryAPIView,ChatHistoryListAPIView,OpenAIStatusAPIView,WelcomeMessageAPIView


urlpatterns = [
    path('search/', SearchAPIView.as_view(), name='search'),
    path('chat/', ChatAPIView.as_view(), name='chat'),
    path('chat/history/', ChatHistoryAPIView.as_view(), name='chat-history'),
    path('chat/conversations/', ChatHistoryListAPIView.as_view(), name='chat-conversation-list'),
    path('health/', HealthCheckAPIView.as_view(), name='health'),
    path('stats/', DocumentStatsAPIView.as_view(), name='document_stats'),
    path('openai/status/', OpenAIStatusAPIView.as_view(), name='openai-status'),
    path('welcome/', WelcomeMessageAPIView.as_view(), name='welcome-message'),
]
