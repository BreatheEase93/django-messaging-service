import secrets

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import CustomUserCreationForm, UserProfileForm
from .models import CustomUser


class RegisterView(CreateView):
    """Контролер для создания пользователя"""

    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False

        token = secrets.token_hex(16)
        user.verification_token = token
        user.save()

        relative_url = reverse("users:verify_email", kwargs={"token": token})
        # Превращаем его в абсолютную ссылку сайта
        absolute_url = self.request.build_absolute_uri(relative_url)

        send_mail(
            subject="Подтверждение регистрации",
            message=f"Здравствуйте, {user.email}! Для завершения регистрации в сервисе рассылок перейдите по ссылке:\n{absolute_url}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return super().form_valid(form)


class ProfileView(UpdateView):
    """Контроллер для редактирования профиля пользователя"""

    model = CustomUser
    form_class = UserProfileForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user


def verify_email(request, token):
    """Активация пользователя при переходе по ссылке из письма."""
    user = get_object_or_404(CustomUser, verification_token=token)
    user.is_active = True
    user.verification_token = None
    user.save()

    messages.success(
        request, "Учетная запись успешно активирована! Теперь вы можете войти."
    )
    return redirect("users:login")
