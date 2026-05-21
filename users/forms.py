from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Форма для создания пользователя"""

    class Meta(UserCreationForm.Meta):
        model = CustomUser

        fields = ("email", "username", "first_name", "last_name", "avatar", "country")

    def __init__(self, *args, **kwargs):
        """Добавляем стили Bootstrap всем полям"""
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class UserProfileForm(forms.ModelForm):
    """Форма, которая позволит менять поля: аватар и страну"""

    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "avatar",
            "country",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
