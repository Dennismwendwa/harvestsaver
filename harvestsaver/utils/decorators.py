from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.http import HttpResponseForbidden

def is_staff(view_func):
    """
    This function ensure only users who are staff get access
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        messages.warning(request, _("You requested for staff only page"))
        return redirect("farm:home")
    return _wrapped_view


