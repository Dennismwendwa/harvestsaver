from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User, Profile, FarmerProfile, BuyerProfile
from accounts.models import EquipmentOwnerProfile


@receiver(post_save, sender=User, dispatch_uid="create_profile")
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

