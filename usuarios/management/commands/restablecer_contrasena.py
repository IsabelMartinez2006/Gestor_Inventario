from getpass import getpass

from django.core.management.base import BaseCommand, CommandError

from usuarios.models import Usuario

MIN_CARACTERES = 12


class Command(BaseCommand):
    help = "Restablece la contraseña de un usuario y le quita el bloqueo por intentos fallidos."

    def add_arguments(self, parser):
        parser.add_argument("correo", help="Correo del usuario")

    def handle(self, *args, **options):
        correo = options["correo"].strip().lower()
        usuario = Usuario.objects.filter(correo=correo).first()
        if usuario is None:
            raise CommandError("No existe un usuario con ese correo.")

        clave = getpass(f"Nueva contraseña (mínimo {MIN_CARACTERES} caracteres): ")
        repetida = getpass("Repite la contraseña: ")
        if len(clave) < MIN_CARACTERES:
            raise CommandError(f"La contraseña debe tener al menos {MIN_CARACTERES} caracteres.")
        if clave != repetida:
            raise CommandError("Las contraseñas no coinciden.")

        usuario.establecer_contrasena(clave)
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        usuario.save()
        self.stdout.write(self.style.SUCCESS(f"Contraseña restablecida y cuenta desbloqueada: {usuario}"))
