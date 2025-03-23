from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path
from . import views
urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.register_user , name='auth_register'),
    path('forget/', views.send_forget_password_email, name='send_forget_password_email'),
    path('reset-password/', views.reset_password, name="change_password"),
    path('change-password/', views.change_password, name="change_password"),
    path('upload_image/', views.upload_image, name='upload_image')
]