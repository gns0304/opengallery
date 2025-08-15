from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, View, TemplateView
from django.shortcuts import redirect, reverse

from artist.models import ArtistApplication, ArtistProfile
from artist.service import process_multiple_approve, process_multiple_reject
from django.db.models import Count, Avg, Max, Q, IntegerField, Min
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta


class AdminOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, "권한이 없는 사용자입니다.")
        return redirect("core:main")

class ApplicationListView(LoginRequiredMixin, AdminOnlyMixin, ListView):
    model = ArtistApplication
    template_name = "admin_panel/applications.html"
    context_object_name = "applications"
    paginate_by = 10

    def get_queryset(self):
        queryset =  (
            ArtistApplication.objects
            .select_related("applicant", "processed_by")
            .order_by("-submitted_at", "-id")
        )

        field = self.request.GET.get("field", "name").strip()
        query = self.request.GET.get("query", "").strip()

        if field and query:

            if field == "name":
                queryset = queryset.filter(name__icontains=query)

            elif field == "email":
                queryset = queryset.filter(email__icontains=query)

            elif field == "phone":
                queryset = queryset.filter(phone__icontains=query)
            else:
                messages.warning(self.request, "지원하지 않는 검색 필드입니다.")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.copy()
        query.pop('page', None)
        context['preserved_query'] = query.urlencode()

        context['page_range'] = context['paginator'].get_elided_page_range(
            context['page_obj'].number,
            on_each_side=1,
            on_ends=1
        )
        context['selected_field'] = self.request.GET.get("field", "")
        context['query'] = self.request.GET.get("query", "")
        return context


class ApplicationMultipleProcessView(LoginRequiredMixin, AdminOnlyMixin, View):
    def post(self, request):

        selected = request.POST.getlist("selected")
        next_url = request.POST.get("next") or reverse("admin_panel:applications")

        if not selected:
            messages.warning(request, "선택된 신청이 없습니다")
            return redirect(next_url)

        action = request.POST.get("action", "").lower()

        if not action:
            messages.warning(request, "처리할 작업을 선택해주세요.")
            return redirect(next_url)

        if action not in ["approve", "reject"]:
            messages.error(request, "잘못된 작업입니다.")
            return redirect(next_url)

        try:
            selected = [int(x) for x in selected]
        except ValueError:
            messages.error(request, "잘못된 신청 ID가 포함되어 있습니다.")
            return redirect(next_url)

        if action == 'approve':
            result = process_multiple_approve(selected, request.user)
            messages.success(
                request,
                f"승인 {len(result.approved)}건, 스킵 {len(result.skipped)}건, 실패 {len(result.failed)}건이 처리되었습니다."
            )
            return redirect(next_url)

        if action == 'reject':
            result = process_multiple_reject(selected, request.user)
            messages.success(
                request,
                f"반려 {len(result.rejected)}건, 스킵 {len(result.skipped)}건이 정상적으로 처리되었습니다."
            )
            return redirect(next_url)

        messages.error(request, "알 수 없는 오류가 발생했습니다.")
        return redirect(next_url)


class DashboardView(LoginRequiredMixin, AdminOnlyMixin, TemplateView):
    template_name = "admin_panel/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pending = ArtistApplication.objects.filter(status="PENDING").count()

        context.update({
            "admin_email": getattr(self.request.user, "email", ""),
            "total_applications": ArtistApplication.objects.count(),
            "approved_applications": ArtistApplication.objects.filter(status="APPROVED").count(),
            "rejected_applications": ArtistApplication.objects.filter(status="REJECTED").count(),
            "pending_applications": pending,
        })
        return context


class ArtistStatsListView(ListView):
    model = ArtistProfile
    template_name = "admin_panel/artist_stats.html"
    context_object_name = "artists"
    paginate_by = 10

    def get_queryset(self):

        now = timezone.now()
        field = self.request.GET.get("field", "name").strip()
        query = self.request.GET.get("query", "").strip()
        recent = now - timedelta(days=30)

        queryset = ArtistProfile.objects.filter(is_approved=True)

        if field == "name":
            queryset = queryset.filter(name__icontains=query)

        elif field == "email":
            queryset = queryset.filter(email__icontains=query)

        elif field == "phone":
            queryset = queryset.filter(phone__icontains=query)
        else:
            messages.warning(self.request, "지원하지 않는 검색 필드입니다.")

        queryset = (
            queryset.annotate(
                works_under_100_count=Count("artworks", filter=Q(artworks__size__lte=100), distinct=True,),
                average_price=Coalesce(Avg("artworks__price"), 0, output_field=IntegerField()),
                exhibitions_count=Count("exhibitions", distinct=True),
                latest_apply_activity = Coalesce(Max("artworks__created_at"), Max("exhibitions__start_date")),
                recent_works = Count("artworks",filter=Q(artworks__created_at__gte=recent),distinct=True),
                min_price = Coalesce(Min("artworks__price"), 0, output_field=IntegerField()),
                max_price = Coalesce(Max("artworks__price"), 0, output_field=IntegerField()),
            ).order_by("-latest_apply_activity", "-id")
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.copy()
        query.pop('page', None)
        context['preserved_query'] = query.urlencode()

        context['page_range'] = context['paginator'].get_elided_page_range(
            context['page_obj'].number,
            on_each_side=1,
            on_ends=1
        )
        context['selected_field'] = self.request.GET.get("field", "")
        context['query'] = self.request.GET.get("query", "")
        return context