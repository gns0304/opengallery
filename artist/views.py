from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from artist.forms import ArtistApplicationForm
from artist.models import ArtistApplication, ArtistProfile
from gallery.models import Artwork, Exhibition
from .forms import ArtworkCreateForm, ExhibitionCreateForm

class ApprovedArtistRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "accounts:login"
    redirect_field_name = "next"

    def test_func(self):
        user = self.request.user
        profile = getattr(user, "artistprofile", None)
        return bool(profile and profile.is_approved)

    def handle_no_permission(self):
        user = self.request.user
        if not user.is_authenticated:
            messages.warning(self.request, "로그인이 필요합니다.")
            return super().handle_no_permission()

        profile = getattr(user, "artistprofile", None)
        if profile is None:
            messages.warning(self.request, "등록된 작가만 접근할 수 있습니다.")
            return redirect("core:main")

        messages.error(self.request, "접근 권한이 없습니다.")
        return redirect("core:main")


class ArtistApplicationCreateView(LoginRequiredMixin, CreateView):
    template_name = "artist/artist_apply.html"
    form_class = ArtistApplicationForm
    success_url = reverse_lazy("core:main")

    login_url = reverse_lazy("accounts:login")
    redirect_field_name = "next"

    def handle_no_permission(self):
        messages.warning(self.request, "로그인이 필요합니다. 로그인 후 다시 시도해주세요.")
        return super().handle_no_permission()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        profile = ArtistProfile.objects.filter(user=request.user, is_approved=True).first()
        if profile:
            messages.info(request, "이미 승인된 작가 계정입니다.")
            return redirect("artist:dashboard")

        pending_exists = ArtistApplication.objects.filter(
            applicant=request.user, status__in=["PENDING", "ERROR", "PROCESSING"]
        ).exists()
        if pending_exists and request.method.lower() == "get":
            messages.info(request, "기접수된 작가 등록 신청이 있습니다. 승인 결과를 기다려주세요.")
            return redirect("core:main")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.applicant = self.request.user

        if ArtistApplication.objects.filter(
            applicant=self.request.user, status="PENDING"
        ).exists():
            messages.warning(self.request, "기접수된 작가 등록 신청이 있습니다. 승인 결과를 기다려주세요.")
            return redirect("core:main")

        messages.success(self.request, "작가 등록 신청이 접수되었어요. 승인 결과를 기다려주세요.")
        return super().form_valid(form)


class ArtworkCreateView(ApprovedArtistRequiredMixin, CreateView):
    model = Artwork
    form_class = ArtworkCreateForm
    template_name = "artist/artwork_apply.html"
    success_url = reverse_lazy("artist:artwork_apply")

    def form_valid(self, form):
        form.instance.artist = self.request.user.artistprofile
        response = super().form_valid(form)
        messages.success(self.request, "작품이 정상적으로 등록되었습니다.")
        return response

    def form_invalid(self, form):
        messages.warning(self.request, "입력값을 확인해주세요.")
        return super().form_invalid(form)


class ExhibitionCreateView(ApprovedArtistRequiredMixin, CreateView):
    model = Exhibition
    form_class = ExhibitionCreateForm
    template_name = "artist/exhibition_apply.html"
    success_url = reverse_lazy("artist:exhibition_apply")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.artist = self.request.user.artistprofile
        response = super().form_valid(form)
        messages.success(self.request, "전시가 등록되었습니다.")
        return response

    def form_invalid(self, form):
        messages.warning(self.request, "입력값을 확인해주세요.")
        return super().form_invalid(form)


class DashboardView(ApprovedArtistRequiredMixin, TemplateView):
    template_name = "artist/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.artistprofile

        context.update({
            "profile_name": getattr(profile, "name", self.request.user.get_username()),
            "profile_email": getattr(profile, "email", self.request.user.email),
            "profile_birth_date": getattr(profile, "birth_date", ""),
            "profile_phone": getattr(profile, "phone", ""),
            "artworks_count": Artwork.objects.filter(artist=profile).count(),
            "exhibitions_count": Exhibition.objects.filter(artist=profile).count(),
            "artworks": Artwork.objects.filter(artist=profile).order_by("-id"),
            "exhibitions": Exhibition.objects.filter(artist=profile).order_by("-start_date", "-id"),
        })
        return context