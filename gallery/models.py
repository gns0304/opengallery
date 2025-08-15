from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from uuid import uuid4
from pathlib import Path

from artist.models import ArtistProfile

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

def validate_image_ext(f):
    ext = Path((getattr(f, "name", "") or "")).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError("지원하지 않는 이미지 형식입니다.")

def validate_image_size(f, max_mb=5):
    if getattr(f, "size", 0) > max_mb * 1024 * 1024:
        raise ValidationError("이미지 크기가 너무 큽니다.")

def artwork_upload_to(instance, filename):
    ext = Path(filename).suffix.lower()
    return f"artworks/A{instance.artist_id}/{uuid4().hex[:8]}{ext}"

def exhibition_upload_to(instance, filename):
    ext = Path(filename).suffix.lower()
    return f"exhibitions/A{instance.artist_id}/{uuid4().hex[:8]}{ext}"

class Artwork(models.Model):
    artist = models.ForeignKey(ArtistProfile, on_delete=models.PROTECT, related_name='artworks', db_index=True)
    title = models.CharField(max_length=64)
    price = models.IntegerField(validators=[MinValueValidator(0)], db_index=True)
    size = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(500)], db_index=True)
    image = models.ImageField(upload_to=artwork_upload_to, blank=True, null=True,
                                  validators=[validate_image_ext, validate_image_size])
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["artist", "title"], name="art_by_artist_title"),
            models.Index(fields=["artist", "-created_at"], name="art_by_artist_recent"),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(price__gte=0), name="price_constraint"),
            models.CheckConstraint(check=models.Q(size__gte=1, size__lte=500), name="size_constraint"),
        ]

    def __str__(self) -> str:
        return f"[{self.artist.name}] {self.title}"


class Exhibition(models.Model):
    artist = models.ForeignKey(ArtistProfile, on_delete=models.PROTECT, related_name="exhibitions", db_index=True)
    title = models.CharField(max_length=64)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    artworks = models.ManyToManyField(Artwork, related_name="exhibitions", blank=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    image = models.ImageField(upload_to=exhibition_upload_to, blank=True, null=True,
                                  validators=[validate_image_ext, validate_image_size])

    class Meta:
        ordering = ["-start_date", "-created_at"]
        indexes = [
            models.Index(fields=["artist", "-start_date"], name="exhibitions_by_artist_recent"),
        ]

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "종료일은 시작일보다 빠를 수 없습니다."})

    def __str__(self) -> str:
        return f"[{self.artist.name}] {self.title}"