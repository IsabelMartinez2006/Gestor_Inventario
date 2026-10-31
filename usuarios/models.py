from datetime import timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone


class Usuario(models.Model):
    MAX_INTENTOS = 3        # intentos fallidos permitidos antes de bloquear
    MINUTOS_BLOQUEO = 15    # cuánto dura el bloqueo

    ROLES = [
        ("administrador", "Administrador"),
        ("empleado", "Empleado"),
    ]

    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(max_length=150, unique=True)
    contrasena = models.CharField(max_length=255)  # aquí se guarda el HASH
    rol = models.CharField(max_length=15, choices=ROLES, default="empleado")
    intentos_fallidos = models.PositiveSmallIntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "usuarios"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.correo})"

    # --- Django REST Framework espera estas dos propiedades en el "usuario" de una petición ---
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    # --- Contraseña  ---
    def establecer_contrasena(self, texto_plano):
        self.contrasena = make_password(texto_plano)

    def verificar_contrasena(self, texto_plano):
        return check_password(texto_plano, self.contrasena)

    # --- Bloqueo por intentos fallidos ---
    def esta_bloqueado(self):
        return self.bloqueado_hasta is not None and self.bloqueado_hasta > timezone.now()

    def registrar_fallo(self):
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= self.MAX_INTENTOS:
            self.bloqueado_hasta = timezone.now() + timedelta(minutes=self.MINUTOS_BLOQUEO)
            self.intentos_fallidos = 0
        self.save(update_fields=["intentos_fallidos", "bloqueado_hasta"])

    def reiniciar_intentos(self):
        if self.intentos_fallidos or self.bloqueado_hasta:
            self.intentos_fallidos = 0
            self.bloqueado_hasta = None
            self.save(update_fields=["intentos_fallidos", "bloqueado_hasta"])
