from functools import wraps

from django.shortcuts import redirect


def login_requerido(vista):
    """Solo deja pasar a quien ya inició sesión; si no, lo manda al login."""
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        if not request.session.get("id_usuario"):
            return redirect("usuarios:login")
        return vista(request, *args, **kwargs)
    return envoltura


def solo_administrador(vista):
    """Igual que login_requerido, pero además exige rol administrador."""
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        if not request.session.get("id_usuario"):
            return redirect("usuarios:login")
        if request.session.get("rol") != "administrador":
            return redirect("usuarios:inicio")
        return vista(request, *args, **kwargs)
    return envoltura
