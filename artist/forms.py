import re
from django import forms
from django.core.validators import RegexValidator
from .models import ArtistApplication

PHONE_RE = r"^\d{3}-\d{3,4}-\d{4}$"

class ArtistApplicationForm(forms.ModelForm):
    name = forms.CharField(
        max_length=16,
        label="이름",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "이름(최대 16자)"}),
    )
    birth_date = forms.DateField(
        label="생년월일",
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control", "placeholder": "YYYY-MM-DD"})
    )
    email = forms.EmailField(
        label="이메일",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "example@domain.com"})
    )
    phone = forms.CharField(
        label="연락처",
        validators=[RegexValidator(regex=PHONE_RE, message="연락처는 000-0000-0000 또는 000-000-0000 형식입니다.")],
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "010-1234-5678"})
    )

    class Meta:
        model = ArtistApplication
        fields = ["name", "gender", "birth_date", "email", "phone"]
        widgets = {
            "gender": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "gender": "성별"
        }
