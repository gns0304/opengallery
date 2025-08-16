from django.views.generic import ListView
from django.db.models import Q, OuterRef, Subquery
from django.utils.http import urlencode
from .models import Artwork
from artist.models import ArtistProfile
from datetime import datetime
from django.contrib import messages

class ArtworkListView(ListView):
    model = Artwork
    template_name = "gallery/artwork_list.html"
    context_object_name = "artworks"
    paginate_by = 24
    ordering = ["-created_at", "-id"]

    @staticmethod
    def _to_int_or_none(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def get_queryset(self):
        queryset = super().get_queryset()

        title = (self.request.GET.get("title") or "").strip()
        price_min = self._to_int_or_none(self.request.GET.get("price_min"))
        price_max = self._to_int_or_none(self.request.GET.get("price_max"))
        size_min = self._to_int_or_none(self.request.GET.get("size_min"))
        size_max = self._to_int_or_none(self.request.GET.get("size_max"))

        if price_min is not None and price_min < 0:
            price_min = 0
        if price_max is not None and price_max < 0:
            price_max = 0
        if size_min is not None:
            size_min = max(1, size_min)
        if size_max is not None:
            size_max = min(500, size_max)

        filters = Q()
        if title:
            queryset = queryset.filter(title__icontains=title)
        if price_min is not None:
            queryset = queryset.filter(price__gte=price_min)
        if price_max is not None:
            queryset = queryset.filter(price__lte=price_max)
        if size_min is not None:
            queryset = queryset.filter(size__gte=size_min)
        if size_max is not None:
            queryset = queryset.filter(size__lte=size_max)

        if filters:
            queryset = queryset.filter(filters)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        title = (self.request.GET.get("title") or "").strip()
        price_min = self._to_int_or_none(self.request.GET.get("price_min"))
        price_max = self._to_int_or_none(self.request.GET.get("price_max"))
        size_min = self._to_int_or_none(self.request.GET.get("size_min"))
        size_max = self._to_int_or_none(self.request.GET.get("size_max"))

        context.update({
            "title": title,
            "price_min": price_min if price_min is not None else "",
            "price_max": price_max if price_max is not None else "",
            "size_min": size_min if size_min is not None else "",
            "size_max": size_max if size_max is not None else "",
        })

        page_obj = context.get("page_obj")
        if page_obj:
            paginator = page_obj.paginator
            context["page_range"] = paginator.get_elided_page_range(
                number=page_obj.number, on_each_side=1, on_ends=1
            )

        preserved_params = {}
        for key in ["title", "price_min", "price_max", "size_min", "size_max"]:
            value = self.request.GET.get(key)
            if value not in [None, ""]:
                preserved_params[key] = value
        context["preserved_query"] = urlencode(preserved_params)

        return context

class ArtistListView(ListView):
    model = ArtistProfile
    template_name = "gallery/artist_list.html"
    context_object_name = "artists"
    paginate_by = 24
    ordering = ["-created_at", "-id"]

    @staticmethod
    def _to_str_or_none(value):
        value = (value or "").strip()
        return value or None

    @staticmethod
    def _to_date_or_none(value):
        if not value:
            return None
        try:
            return datetime.strptime(value.strip(), "%Y-%m-%d").date()
        except ValueError:
            return None

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_approved=True)

        name = self._to_str_or_none(self.request.GET.get("name"))
        gender = self._to_str_or_none(self.request.GET.get("gender"))
        birth_date_raw = self.request.GET.get("birth_date")
        birth_date = self._to_date_or_none(birth_date_raw)
        email = self._to_str_or_none(self.request.GET.get("email"))
        phone = self._to_str_or_none(self.request.GET.get("phone"))

        if name:
            queryset = queryset.filter(name__icontains=name)
        if gender:
            queryset = queryset.filter(gender=gender)
        if birth_date:
            queryset = queryset.filter(birth_date=birth_date)
        if email:
            queryset = queryset.filter(email__icontains=email)
        if phone:
            queryset = queryset.filter(phone__icontains=phone)

        latest_with_image = (
            Artwork.objects
            .filter(artist=OuterRef("pk"))
            .filter(image__isnull=False)
            .exclude(image="")
            .order_by("-created_at", "-id")
            .values("image")[:1]
        )
        queryset = queryset.annotate(
            latest_artwork_image=Subquery(latest_with_image)
        )
        return queryset

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)

            name = self._to_str_or_none(self.request.GET.get("name")) or ""
            gender = self._to_str_or_none(self.request.GET.get("gender")) or ""
            birth_date = self._to_str_or_none(self.request.GET.get("birth_date")) or ""
            email = self._to_str_or_none(self.request.GET.get("email")) or ""
            phone = self._to_str_or_none(self.request.GET.get("phone")) or ""

            context.update({
                "name": name,
                "gender": gender,
                "birth_date": birth_date,
                "email": email,
                "phone": phone,
            })

            page_obj = context.get("page_obj")
            if page_obj:
                paginator = page_obj.paginator
                context["page_range"] = paginator.get_elided_page_range(
                    number=page_obj.number, on_each_side=1, on_ends=1
                )

            preserved_params = {}
            for key in ["name", "gender", "birth_date", "email", "phone"]:
                value = self.request.GET.get(key)
                if key == "birth_date":
                    if self._to_date_or_none(value):
                        preserved_params[key] = value
                else:
                    if value not in [None, ""]:
                        preserved_params[key] = value
            context["preserved_query"] = urlencode(preserved_params)
            return context