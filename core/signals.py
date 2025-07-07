from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Complaint, Comment, Notification
from .models import Profile
from django.contrib.auth.models import User


@receiver(post_save, sender=Complaint)
def complaint_created(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            message=f" Your complaint '{instance.title}' was submitted."
        )
    else:
        # Status change logic
        if instance.status == 'resolved':
            Notification.objects.create(
                user=instance.user,
                message=f"Your complaint '{instance.title}' was resolved."
            )
        elif instance.status == 'escalated':
            Notification.objects.create(
                user=instance.user,
                message=f" Your complaint '{instance.title}' has been escalated."
            )


@receiver(post_save, sender=Comment)
def comment_notification(sender, instance, created, **kwargs):
    if created and not instance.is_internal:
        Notification.objects.create(
            user=instance.complaint.user,
            message="🗨️ You have a new reply from admin."
        )

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()