from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings
from django.db.models import UniqueConstraint, Q

GENDER_CHOICES = (("M", "남자"), ("F", "여자"))

phone_validator = RegexValidator(
    regex=r"^\d{3}-\d{3,4}-\d{4}$",
    message="연락처는 000-0000-0000 또는 000-000-0000 형식이어야 합니다.",
)

class ArtistProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=16)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField()
    email = models.EmailField()
    phone = models.CharField(max_length=13, validators=[phone_validator,])
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["is_approved", "-created_at", "-id"])
        ]

    def __str__(self):
        return f"{self.name} ({self.user.email})"

class ArtistApplication(models.Model):
    STATUS_CHOICES = (("PENDING", "대기"), ("PROCESSING", "처리중"), ("APPROVED", "승인"), ("REJECTED", "반려"),
                      ("ERROR", "오류"))
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="artist_apps"
    )
    name = models.CharField(max_length=16)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField()
    email = models.EmailField()
    phone = models.CharField(max_length=13, validators=[phone_validator, ])
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING",
        db_index=True
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="processed_artist_apps"
    )
    last_error_message = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-submitted_at", "-id"]
        indexes = [models.Index(fields=["status", "-submitted_at", "-id"])]
        constraints = [
            UniqueConstraint(fields=["applicant"], condition=~Q(status="REJECTED"),
                             name="unique_applicant_without_rejected",
                             )
        ]

    def __str__(self):
        return f"{self.name} / {self.get_status_display()}"

