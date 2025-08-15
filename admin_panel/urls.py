from django.urls import path
from . import views

app_name = "admin_panel"

urlpatterns = [
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("artist/applications/", views.ApplicationListView.as_view(), name="applications"),
    path("artist/applications/process/", views.ApplicationMultipleProcessView.as_view(), name="application_process"),
    path("artist/stats/", views.ArtistStatsListView.as_view(), name="artist_stats"),
]