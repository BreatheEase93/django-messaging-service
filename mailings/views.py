from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
)

from .models import Message


class MessagetListView(LoginRequiredMixin, ListView):
    """Просмотр списка писим."""

    model = Message
    template_name = "malings/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        """Возвращает только те письма, которые принадлежат текущему пользователю."""
        # Менеджеры могут просматривать вообще все сообщения
        if self.request.user.groups.filter(name="Менеджеры").exists():
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)
