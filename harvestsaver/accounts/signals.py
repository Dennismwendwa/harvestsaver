from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User, FarmerProfile, BuyerProfile, EquipmentOwnerProfile
from payment.models import Account, accounts_number


@receiver(post_save, sender=User, dispatch_uid="create_profile")
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_farmer:
            FarmerProfile.objects.create(user=instance)
        elif instance.is_customer:
            BuyerProfile.objects.create(user=instance)
        elif instance.is_equipment_owner:
            EquipmentOwnerProfile.objects.create(user=instance)

        Account.objects.create(user=instance,
                               account_number=accounts_number(instance.pk),
                               account_name= f"{instance.first_name} {instance.last_name}")


@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.is_farmer:
        instance.farmer_profile.save()
    elif instance.is_customer:
        instance.buyer_profile.save()
    elif instance.is_equipment_owner:
        instance.equipment_owner_profile.save()
    instance.account.save()

