from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User, Profile, FarmerProfile, BuyerProfile
from payment.models import Account, accounts_number


@receiver(post_save, sender=User, dispatch_uid="create_profile")
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        Account.objects.create(user=instance,
                               account_number=accounts_number(instance.pk),
                               account_name= f"{instance.first_name} {instance.last_name}")


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
    instance.account.save()

