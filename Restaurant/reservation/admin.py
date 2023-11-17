# admin.py
from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'seats', 'reservation_date', 'reservation_time', 'special_request']
    search_fields = ['user__username', 'reservation_date', 'reservation_time']
    list_filter = ['reservation_date', 'reservation_time']
    ordering = ['reservation_date', 'reservation_time']

