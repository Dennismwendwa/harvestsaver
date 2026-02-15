from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    """Get a value from a dictionary using a key."""
    try:
        return d.get(int(key), 0)
    except (KeyError, ValueError, TabError):
        return 0