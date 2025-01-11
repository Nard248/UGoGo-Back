# items/admin.py

from django.contrib import admin
from .models import Item, Request

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'weight', 'dimensions', 'created_at')
    search_fields = ('name', 'user__email')


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'offer', 'user', 'suggested_price', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('item__name', 'user__email', 'offer__id')
