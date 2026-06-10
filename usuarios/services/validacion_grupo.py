from django.core.exceptions import PermissionDenied
from functools import wraps

from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect

def grupos_requeridos(*grupos):

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                messages.warning(
                    request,
                    "Debe iniciar sesión para acceder al sistema."
                )
                return redirect('usuarios:login')

            if request.user.groups.filter(
                name__in=grupos
            ).exists():
                return view_func(request, *args, **kwargs)

            messages.error(
                request,
                "No tiene permisos para acceder a esta sección."
            )

            return redirect('login')

        return wrapper

    return decorator