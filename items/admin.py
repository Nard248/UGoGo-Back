# items/admin.py

from django.contrib import admin
from .models.items import Item
from flight_requests.models.request import Request


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'weight', 'dimensions', 'created_at')
    search_fields = ('name', 'user__email')

