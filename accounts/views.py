from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.views import View
from .forms import SignupForm, EmailAuthenticationForm

class SignupView(View):
    def get(self, request):
        return render(request, "accounts/signup.html", {"form": SignupForm()})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
        return render(request, "accounts/signup.html", {"form": form})

class SigninView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailAuthenticationForm

class SignoutView(LogoutView):
    pass
