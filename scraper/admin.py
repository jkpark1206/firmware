from django.contrib import admin

from .models import Firmware


class FirmwareAdmin(admin.ModelAdmin):
    list_display = ('id', 'vendor', 'product', 'version', 'device_class', 'url', 'file_path')
    search_fields = ('vendor', 'product')


admin.site.register(Firmware, FirmwareAdmin)
