from django.contrib.auth.models import auth, Group, Permission
from django.contrib.contenttypes.models import ContentType

def create_group_and_permission(role, user):
    """
    We are creating group, and
    add permissions to the group
    and we add user to the group
    """
    if role == "farmer":
        model = "product"
        app_name = "farm"
    elif role == "equipment_owner":
        model = "equipment"
        app_name = "farm"
    
    role = role.capitalize()
    try:
        group = Group.objects.get(name=role)
    except Group.DoesNotExist:
        group = Group.objects.create(name=role)

    content_type = ContentType.objects.get(app_label=app_name, model=model)

    try:
        view_permission = Permission.objects.get(
            codename=f"view_{model.lower()}",
            content_type=content_type
            )
    except Permission.DoesNotExist:
        view_permission = Permission.objects.create(
            codename=f"view_{model.lower()}",
            name=f"Can view {model}",
            content_type=content_type,
            )
    group.permissions.add(view_permission)
    group.user_set.add(user)