from getpass import getpass

from django.core.management.base import BaseCommand, CommandError

from usuarios.models import Usuario

MIN_CARACTERES = 12


class Command(BaseCommand):
    help = "Crea un usuario pidiendo los datos en la terminal (la contraseña se guarda hasheada)."

    def handle(self, *args, **options):
        nombre = input("Nombre completo: ").strip()
        correo = input("Correo electrónico: ").strip().lower()
        rol = input("Rol (administrador/empleado) [empleado]: ").strip().lower() or "empleado"
        clave = getpass(f"Contraseña (mínimo {MIN_CARACTERES} caracteres): ")
        repetida = getpass("Repite la contraseña: ")

        if not nombre or not correo:
            raise CommandError("El nombre y el correo son obligatorios.")
        if rol not in ("administrador", "empleado"):
            raise CommandError("El rol debe ser 'administrador' o 'empleado'.")
        if Usuario.objects.filter(correo=correo).exists():
            raise CommandError("Ya existe un usuario con ese correo.")
        if len(clave) < MIN_CARACTERES:
            raise CommandError(f"La contraseña debe tener al menos {MIN_CARACTERES} caracteres.")
        if clave != repetida:
            raise CommandError("Las contraseñas no coinciden.")

        usuario = Usuario(nombre=nombre, correo=correo, rol=rol)
        usuario.establecer_contrasena(clave)
        usuario.save()
        self.stdout.write(self.style.SUCCESS(f"Usuario creado: {usuario}"))
