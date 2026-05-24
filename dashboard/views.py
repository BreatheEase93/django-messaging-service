from django.core.cache import cache
from django.views.generic import TemplateView

from clients.models import Client
from mailings.models import Mailing


class DashboardView(TemplateView):
    """Контроллер главной страницы с отображением кешированной статистики."""

    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Пытаемся достать готовую статистику из кэша Redis
        stats = cache.get("dashboard_stats")

        # Если в кэше ничего нет (он устарел или это первый запуск) — считаем из БД
        if not stats:
            stats = {
                "total_mailings": Mailing.objects.count(),
                "active_mailings": Mailing.objects.filter(status="started").count(),
                "total_clients": Client.objects.count(),
            }
            cache.set("dashboard_stats", stats, 600)

        # Передаем данные из словаря в контекст шаблона HTML
        context.update(stats)
        return context
