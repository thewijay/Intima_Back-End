from django.urls import path
from .views import RegisterView, LoginView, ProfileView, CompleteProfileView, UpdateProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/complete/', CompleteProfileView.as_view(), name='complete-profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update-profile'),
]
