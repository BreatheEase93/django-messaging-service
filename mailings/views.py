from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .models import Mailing, Message
from .services import send_mailing  # Импортируем наш движок отправки


# ==================== КОНТРОЛЛЕРЫ СООБЩЕНИЙ ====================
class MessageListView(LoginRequiredMixin, ListView):
    """Просмотр списка писем."""

    model = Message
    template_name = "mailings/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        if self.request.user.groups.filter(name="Менеджеры").exists():
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр конкретного письма."""

    model = Message
    template_name = "mailings/message_detail.html"

    def get_queryset(self):
        if self.request.user.groups.filter(name="Менеджеры").exists():
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Создание нового письма."""

    model = Message
    fields = ("subject", "body")
    template_name = "mailings/message_form.html"
    success_url = reverse_lazy("mailings:message_list")

    def form_valid(self, form):
        message_obj = form.save(commit=False)
        message_obj.owner = self.request.user
        message_obj.save()
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование письма."""

    model = Message
    fields = ("subject", "body")
    template_name = "mailings/message_form.html"
    success_url = reverse_lazy("mailings:message_list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление письма из базы данных."""

    model = Message
    template_name = "mailings/message_confirm_delete.html"
    success_url = reverse_lazy("mailings:message_list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


# ==================== КОНТРОЛЛЕРЫ РАССЫЛОК ====================
class MailingListView(LoginRequiredMixin, ListView):
    """Просмотр списка рассылок с динамическим обновлением статусов."""

    model = Mailing
    template_name = "mailings/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        if self.request.user.groups.filter(name="Менеджеры").exists():
            queryset = Mailing.objects.all()
        else:
            queryset = Mailing.objects.filter(owner=self.request.user)

        # Твоя идея: обновляем статусы на лету при просмотре списка
        for mailing in queryset:
            mailing.update_status()
        return queryset


class MailingDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр конкретной рассылки."""

    model = Mailing
    template_name = "mailings/mailing_detail.html"

    def get_object(self, queryset=None):
        # Твоя идея: пересчёт статуса при открытии конкретной страницы
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

    def get_queryset(self):
        if self.request.user.groups.filter(name="Менеджеры").exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    """Создание новой рассылки (Исправили опечатку в имени и поля)."""

    model = Mailing
    fields = ("start_time", "end_time", "message", "recipients")
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def form_valid(self, form):
        mailing_obj = form.save(commit=False)
        mailing_obj.owner = self.request.user
        mailing_obj.save()
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование рассылки (Исправили поля)."""

    model = Mailing
    fields = ("start_time", "end_time", "message", "recipients")
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление рассылки (Исправили имя класса и редирект)."""

    model = Mailing
    template_name = "mailings/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


# ==================== РУЧНОЙ ЗАПУСК РАССЫЛКИ  ====================
class MailingStartView(LoginRequiredMixin, View):
    """Контроллер для обработки клика по кнопке 'Запустить рассылку'."""

    def post(self, request, pk, *args, **kwargs):
        # Менеджеры не могут запускать отправку, только владельцы!
        mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)

        success, result_message = send_mailing(mailing)

        if success:
            messages.success(request, result_message)
        else:
            messages.error(request, result_message)

        return redirect("mailings:mailing_detail", pk=pk)
