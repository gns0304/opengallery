from django.urls import path
from .views import ArtistApplicationCreateView
app_name = "artist"

urlpatterns = [
    path("apply/", ArtistApplicationCreateView.as_view(), name="apply")
]