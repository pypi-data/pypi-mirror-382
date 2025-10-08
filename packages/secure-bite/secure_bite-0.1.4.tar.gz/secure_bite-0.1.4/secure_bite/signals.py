from django.dispatch import Signal, receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail
from secure_bite.models import SocialAccount

# Signal fired when a new social account is linked
user_account_created = Signal()

@receiver(user_account_created)
def send_welcome_email(sender, user, provider=None, **kwargs):
    """Send email when a user is created via social login or normal registration."""
    if not user.email:
        return
    print(sender)
    subject = "Welcome to SecureBite"
    if provider:
        message = f"Hello {user.get_full_name() or user.username}, your account has been created using {provider.capitalize()} login."
    else:
        message = f"Hello {user.get_full_name() or user.username}, your account has been created."

    send_mail(
        subject=subject,
        message=message,
        from_email="no-reply@securebite.com",
        recipient_list=[user.email],
        fail_silently=True,
    )

@receiver(post_save, sender=SocialAccount)
def trigger_user_created_signal(sender, instance, created, **kwargs):
    """Fire user_account_created when a new social account is created."""
    if created:
        user_account_created.send(
            sender=instance,
            user=instance.user,
            provider=instance.provider,
        )