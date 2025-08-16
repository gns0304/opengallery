from django.urls import path
from .views import ArtworkListView, ArtistListView

app_name = "gallery"

urlpatterns = [
    path('artworks/', ArtworkListView.as_view(), name='artwork_list'),
path('artists/', ArtistListView.as_view(), name='artist_list'),
]