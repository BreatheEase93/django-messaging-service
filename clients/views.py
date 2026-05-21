from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .models import Client


class ClientListView(LoginRequiredMixin, ListView):
    """Просмотр списка всех клиентов текущего пользователя."""

    model = Client
    template_name = "clients/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        """Возвращает только тех клиентов, которые принадлежат текущему пользователю."""
        # Менеджеры могут просматривать вообще всех клиентов в системе
        if self.request.user.groups.filter(name="Менеджеры").exists():
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class ClientDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр конкретного клиента."""

    model = Client
    template_name = "clients/client_detail.html"

    def get_queryset(self):
        """Ограничивает доступ к деталям чужих клиентов."""
        if self.request.user.groups.filter(name="Менеджеры").exists():
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    """Создание нового клиента."""

    model = Client
    fields = ("name", "email", "comment")
    template_name = "clients/client_form.html"
    success_url = reverse_lazy("clients:list")

    def form_valid(self, form):
        """Автоматически назначает текущего пользователя владельцем клиента."""
        client = form.save(commit=False)
        client.owner = self.request.user
        client.save()
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование данных клиента."""

    model = Client
    fields = ("name", "email", "comment")
    template_name = "clients/client_form.html"
    success_url = reverse_lazy("clients:list")

    def get_queryset(self):
        """Запрещает обычным пользователям редактировать чужих клиентов."""
        # Менеджерымогут только СМОТРЕТЬ, но не редактировать чужие данные!
        # Поэтому для них и обычных юзеров возвращаем только их собственных клиентов для изменения
        return Client.objects.filter(owner=self.request.user)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление клиента из базы данных."""

    model = Client
    template_name = "clients/client_confirm_delete.html"
    success_url = reverse_lazy("clients:list")

    def get_queryset(self):
        """Запрещает удалять чужих клиентов."""
        return Client.objects.filter(owner=self.request.user)
