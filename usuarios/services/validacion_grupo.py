from django.core.exceptions import PermissionDenied
from functools import wraps

def grupos_requeridos(*grupos):

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                raise PermissionDenied

            if request.user.groups.filter(
                name__in=grupos
            ).exists():
                return view_func(request, *args, **kwargs)

            raise PermissionDenied

        return wrapper

    return decorator