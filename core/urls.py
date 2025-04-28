from django.urls import path
from .views import version_info
urlpatterns = [
    path('latest-version/', version_info, name='item-list-create'),

]
