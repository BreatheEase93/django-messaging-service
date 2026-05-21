from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "owner")
    search_fields = ("email", "name", "owner__email")
    list_filter = ("owner",)
    raw_id_fields = ("owner",)

    def save_model(self, request, obj, form, change):

        if not change:
            obj.owner = request.user

        super().save_model(request, obj, form, change)
