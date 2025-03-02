from django.urls import path

from .views.views import RegisterUserView, CustomTokenObtainPairView, LogOutView, VerifyEmailView, ResendVerificationCodeView, SendResedPasswordLink
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView

from .views.admin_login import AdminLoginView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin-login/', AdminLoginView.as_view(), name='admin_login'),
    path('token/logout/', LogOutView.as_view(), name='token_logout'),
    path('verfiy-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification-email/', ResendVerificationCodeView.as_view(), name='resend-verification-email'),
    path('forgot-password/', SendResedPasswordLink.as_view(), name='forgot-password'),

]
