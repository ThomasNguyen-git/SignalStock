# main_app/admin.py

from django.contrib import admin
from .models import DataSheet

@admin.register(DataSheet)
class DataSheetAdmin(admin.ModelAdmin):
    list_display = ('sheet_name', 'symbol', 'volume', 'signal', 'date')  # Thêm cột date
    list_filter = ('sheet_name', 'date')  # Thêm filter theo sheet_name và date
    search_fields = ('symbol', 'signal')  # Thêm khả năng tìm kiếm theo symbol và signal
