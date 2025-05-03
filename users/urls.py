from django.urls import path

from .views.admin_user_verification_view import VerifyUserPassportView
from .views.pid_verification import PIDUploadView
from .views.views import RegisterUserView, CustomTokenObtainPairView, LogOutView, VerifyEmailView, ResendVerificationCodeView, SendResedPasswordLink, UserInfoView, UserListView
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from .views.card import SendCardVerificationEmailView

from .views.admin_login import AdminLoginView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserInfoView.as_view(), name='me'),
    path('admin-login/', AdminLoginView.as_view(), name='admin_login'),
    path('token/logout/', LogOutView.as_view(), name='token_logout'),
    path('verfiy-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification-email/', ResendVerificationCodeView.as_view(), name='resend-verification-email'),
    path('forgot-password/', SendResedPasswordLink.as_view(), name='forgot-password'),
    path('admin/verify-user-passport/', VerifyUserPassportView.as_view(), name='forgot-password'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('pid-upload/', PIDUploadView.as_view(), name='user-list'),
    path('send-verification-code/', SendCardVerificationEmailView.as_view(), name='send-verification-code'),
    # path('bankcards/', BankCardListView.as_view(), name='bankcard-list'),  # GET and POST
    # path('bankcards/<int:pk>/', BankCardDetailView.as_view(), name='bankcard-detail'),  # GET, PUT, PATCH, DELETE

]
