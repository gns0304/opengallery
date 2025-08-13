from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.views import View
from .forms import SignupForm, EmailAuthenticationForm

class RedirectIfAuthenticatedMixin:
    redirect_url = "/"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.warning(request, "이미 로그인되어 있습니다.")
            return redirect(self.redirect_url)
        return super().dispatch(request, *args, **kwargs)

class SignupView(RedirectIfAuthenticatedMixin, View):
    def get(self, request):
        return render(request, "accounts/signup.html", {"form": SignupForm()})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
        return render(request, "accounts/signup.html", {"form": form})

class SigninView(RedirectIfAuthenticatedMixin, LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailAuthenticationForm

class SignoutView(LogoutView):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "로그아웃되었습니다.")
        return super().dispatch(request, *args, **kwargs)
