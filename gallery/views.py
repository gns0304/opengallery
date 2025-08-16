from django.views.generic import ListView
from django.db.models import Q
from django.utils.http import urlencode
from .models import Artwork

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