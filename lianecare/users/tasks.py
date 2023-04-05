from allauth.account.models import EmailAddress
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone

from config import celery_app

User = get_user_model()


@celery_app.task()
def second_send_email_verify():
    """Sends a second verification email to all users who have not yet verified their email after 24 hours."""
    time_threshold = datetime.now() - timedelta(hours=24)
    emails = EmailAddress.objects.filter(verified=False, user__date_joined__lte=time_threshold)
    for email in emails:
        email.send_confirmation()
    return emails.count()


@celery_app.task()
def delete_unverified_users():
    """It deletes all users who have not verified their email within 72 hours."""
    total_obj_deleted, obj_deleted = User.objects.filter(emailaddress__verified=False,
                                        date_joined__lte=timezone.now() - timedelta(hours=72)
                                        ).delete()
    return total_obj_deleted
