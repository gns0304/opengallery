from django.contrib import admin
from .models import ArtistApplication, ArtistProfile

admin.site.register(ArtistApplication)
admin.site.register(ArtistProfile)