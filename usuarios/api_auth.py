"""Autenticación y permisos de la API REST, basados en la sesión del login."""
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import Usuario


class SesionUsuarioAuthentication(SessionAuthentication):
    """Identifica al usuario por la cookie de sesión. En POST/PUT/PATCH/DELETE exige token ."""

    def authenticate(self, request):
        id_usuario = request._request.session.get("id_usuario")
        if not id_usuario:
            return None
        usuario = Usuario.objects.filter(pk=id_usuario).first()
        if usuario is None:
            return None
        self.enforce_csrf(request)
        return (usuario, None)


class AccesoPorRol(BasePermission):
    """Lectura: cualquier usuario con sesión. Escritura: solo administrador."""

    def has_permission(self, request, view):
        usuario = request.user
        if not getattr(usuario, "is_authenticated", False):
            return False
        if request.method in SAFE_METHODS:
            return True
        return usuario.rol == "administrador"
