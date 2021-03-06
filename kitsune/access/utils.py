from django.contrib.contenttypes.models import ContentType

from authority.sites import get_check
from authority.models import Permission


def has_perm_or_owns(user, perm, obj, perm_obj,
                     field_name='creator'):
    """Given a user, a permission, an object (obj) and another object to check
    permissions against (perm_obj), return True if the user has perm on
    obj."""
    if user.is_anonymous():
        return False

    if hasattr(obj, '%s_id' % field_name):
        if getattr(obj, '%s_id' % field_name) == user.pk:
            return True
    elif user == getattr(obj, field_name):
        return True

    check = get_check(user, perm)
    return user.has_perm(perm) or (check and check(perm_obj))


def has_perm(user, perm, obj):
    """Return whether a user has a permission globally or on a given object."""
    check = get_check(user, perm)  # None sometimes
    return user.has_perm(perm) or (check and check(obj))


def perm_is_defined_on(perm, obj):
    """Return whether an object has an authority permission that references it.

    If it doesn't, we sometimes treat that permission as free to everyone,
    since the auth backends we currently use have no concept of granting a
    permission to the world.

    Considers only approved permissions to exist.

    """
    return Permission.objects.filter(
        codename=perm,
        content_type=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
        approved=True).exists()
