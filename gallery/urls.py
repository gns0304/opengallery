from django.urls import path
from .views import ArtworkListView

app_name = "gallery"

urlpatterns = [
    path('artworks/', ArtworkListView.as_view(), name='artwork_list'),
]