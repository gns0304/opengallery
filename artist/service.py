from django.db import transaction, IntegrityError
from django.utils import timezone
from .models import ArtistApplication, ArtistProfile


class ProcessResult:
    def __init__(self):
        self.approved = []
        self.skipped = []
        self.failed = []


def process_single_application(application: ArtistApplication, admin_user):
    with transaction.atomic():
        application = (ArtistApplication.objects.select_for_update().select_related('applicant').get(pk=application.pk))

        if application.status not in ("PENDING", "ERROR"):
            return "SKIPPED"

        application.status = "PROCESSING"
        application.processed_by = admin_user
        application.processed_at = timezone.now()
        application.last_error_message = ""
        application.save(update_fields=["status", "processed_by", "processed_at", "last_error_message"])

        try:
            _, created = ArtistProfile.objects.get_or_create(
                user=application.applicant,
                defaults={
                "name": application.name,
                "gender": application.gender,
                "birth_date": application.birth_date,
                "email": application.email,
                "phone": application.phone,
                "is_approved": True
                }
            )
        except IntegrityError:
            created = False

        application.status = "APPROVED"
        if not created:
            application.last_error_message = "이미 프로필이 존재합니다."
            application.save(update_fields=["status", "last_error_message"])
            return "SKIPPED"

        application.save(update_fields=["status"])
        return "APPROVED"


def process_multiple_approve(application_ids, admin_user):
    result = ProcessResult()
    for app in ArtistApplication.objects.filter(pk__in=application_ids).only("id"):
        try:
            return_message = process_single_application(app, admin_user)
            if return_message == "APPROVED":
                result.approved.append(app.id)
            else:
                result.skipped.append(app.id)
        except IntegrityError as e:
            ArtistApplication.objects.filter(pk=app.id).update(
                status="ERROR", last_error_message=f"IntegrityError: {e}"
            )
            result.failed.append(app.id)
        except Exception as e:
            ArtistApplication.objects.filter(pk=app.id).update(
                status="ERROR", last_error_message=f"Error: {e}"
            )
            result.failed.append(app.id)
    return result