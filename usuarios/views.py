from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .decorators import login_requerido, solo_administrador
from .models import Usuario

# Un solo mensaje para cualquier fallo no revela si el correo existe o si la cuenta está bloqueada.
MENSAJE_FALLO = (
    "No pudimos iniciar sesión. Revisa tus datos; tras "
    f"{Usuario.MAX_INTENTOS} intentos fallidos la cuenta se bloquea "
    f"{Usuario.MINUTOS_BLOQUEO} minutos."
)


def login_vista(request):
    if request.session.get("id_usuario"):
        return redirect("usuarios:inicio")

    error = None
    correo = ""

    if request.method == "POST":
        correo = request.POST.get("correo", "").strip().lower()
        contrasena = request.POST.get("contrasena", "")
        usuario = Usuario.objects.filter(correo=correo).first()

        if usuario and not usuario.esta_bloqueado():
            if usuario.verificar_contrasena(contrasena):
                usuario.reiniciar_intentos()
                request.session.cycle_key()  # sesión nueva al entrar
                request.session["id_usuario"] = usuario.id_usuario
                request.session["nombre"] = usuario.nombre
                request.session["rol"] = usuario.rol
                request.session["iniciales"] = "".join(p[0] for p in usuario.nombre.split()[:2]).upper()
                return redirect("usuarios:inicio")
            usuario.registrar_fallo()

        error = MENSAJE_FALLO

    return render(request, "login.html", {"error": error, "correo": correo})


@require_POST
def logout_vista(request):
    request.session.flush()
    return redirect("usuarios:login")


@login_requerido
def inicio(request):
    """Pantalla a la que se llega después de iniciar sesión.

    Por ahora es provisional
    """
    return render(request, "en_construccion.html", {"seccion": "resumen", "titulo": "Resumen"})


@solo_administrador
def listado(request):
    return render(request, "en_construccion.html", {"seccion": "usuarios", "titulo": "Usuarios"})
