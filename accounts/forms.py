from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "이메일"
        self.fields["password1"].label = "비밀번호"
        self.fields["password2"].label = "비밀번호 확인"

        self.fields["email"].widget = forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "이메일",
            "autocomplete": "email",
        })
        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "비밀번호",
            "autocomplete": "new-password",
        })
        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "비밀번호 확인",
            "autocomplete": "new-password",
        })

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise forms.ValidationError("이메일은 필수입니다.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("이미 사용 중인 이메일입니다.")
        return email

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="이메일",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "이메일",
            "autocomplete": "email",
        })
    )

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()