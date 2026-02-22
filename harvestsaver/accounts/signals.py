from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from payment.models import Account


@receiver(post_save, sender=User, dispatch_uid="create_profile")
def create_profile(sender, instance, created, **kwargs):
    if created:

        Account.objects.create(user=instance,
                               account_name= f"{instance.first_name} {instance.last_name}")


@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if not created:
        return
    instance.account.save()

