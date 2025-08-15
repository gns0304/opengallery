from django.urls import path
from .views import ArtistApplicationCreateView, ArtworkCreateView, ExhibitionCreateView, DashboardView
app_name = "artist"

urlpatterns = [
    path("apply/", ArtistApplicationCreateView.as_view(), name="apply"),
    path("artwork/apply/", ArtworkCreateView.as_view(), name="artwork_apply"),
    path("exhibition/apply/", ExhibitionCreateView.as_view(), name="exhibition_apply"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]