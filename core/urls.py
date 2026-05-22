from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls", namespace="users")),
    path("clients/", include("clients.urls", namespace="clients")),
    path("mailings/", include("mailings.urls", namespace="mailings")),
]
