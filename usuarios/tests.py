from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Usuario

CLAVE = "ClaveDePrueba#2026"


def crear_usuario(correo="ana@ejemplo.com", rol="administrador", nombre="Ana García"):
    usuario = Usuario(nombre=nombre, correo=correo, rol=rol)
    usuario.establecer_contrasena(CLAVE)
    usuario.save()
    return usuario


class LoginTests(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()
        self.url = reverse("usuarios:login")

    def test_contrasena_se_guarda_hasheada(self):
        self.assertTrue(self.usuario.contrasena.startswith("pbkdf2_sha256$"))
        self.assertNotIn(CLAVE, self.usuario.contrasena)

    def test_login_correcto_entra_al_inicio(self):
        r = self.client.post(self.url, {"correo": "ANA@ejemplo.com", "contrasena": CLAVE})
        self.assertRedirects(r, reverse("usuarios:inicio"))
        self.assertEqual(self.client.session["rol"], "administrador")
        self.assertEqual(self.client.session["iniciales"], "AG")

    def test_tres_fallos_bloquean_la_cuenta_aunque_luego_use_la_clave_correcta(self):
        for _ in range(3):
            r = self.client.post(self.url, {"correo": "ana@ejemplo.com", "contrasena": "incorrecta"})
            self.assertEqual(r.status_code, 200)
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.esta_bloqueado())

        r = self.client.post(self.url, {"correo": "ana@ejemplo.com", "contrasena": CLAVE})
        self.assertEqual(r.status_code, 200)
        self.assertNotIn("id_usuario", self.client.session)

    def test_el_bloqueo_termina_con_el_tiempo(self):
        self.usuario.bloqueado_hasta = timezone.now() - timedelta(minutes=1)
        self.usuario.save()
        r = self.client.post(self.url, {"correo": "ana@ejemplo.com", "contrasena": CLAVE})
        self.assertRedirects(r, reverse("usuarios:inicio"))

    def test_un_acierto_reinicia_el_contador(self):
        for _ in range(2):
            self.client.post(self.url, {"correo": "ana@ejemplo.com", "contrasena": "mal"})
        self.client.post(self.url, {"correo": "ana@ejemplo.com", "contrasena": CLAVE})
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.intentos_fallidos, 0)

    def test_mensaje_igual_si_el_correo_no_existe(self):
        r1 = self.client.post(self.url, {"correo": "nadie@ejemplo.com", "contrasena": "x"})
        r2 = self.client.post(self.url, {"correo": "ana@ejemplo.com", "contrasena": "x"})
        self.assertEqual(r1.context["error"], r2.context["error"])

    def test_logout_solo_por_post_y_limpia_la_sesion(self):
        self.client.post(self.url, {"correo": "ana@ejemplo.com", "contrasena": CLAVE})
        self.assertEqual(self.client.get(reverse("usuarios:logout")).status_code, 405)
        self.client.post(reverse("usuarios:logout"))
        self.assertNotIn("id_usuario", self.client.session)

    def test_paginas_protegidas_redirigen_al_login(self):
        for nombre in ("usuarios:inicio", "usuarios:listado"):
            self.assertRedirects(self.client.get(reverse(nombre)), self.url)


class PermisosPorRolTests(TestCase):
    def setUp(self):
        crear_usuario("ana@ejemplo.com", "administrador")
        crear_usuario("luis@ejemplo.com", "empleado", "Luis Martínez")

    def entrar(self, correo):
        self.client.post(reverse("usuarios:login"), {"correo": correo, "contrasena": CLAVE})

    def test_administrador_ve_usuarios_en_el_menu_y_entra(self):
        self.entrar("ana@ejemplo.com")
        r = self.client.get(reverse("usuarios:inicio"))
        self.assertContains(r, "Usuarios")
        self.assertEqual(self.client.get(reverse("usuarios:listado")).status_code, 200)

    def test_empleado_no_ve_ni_entra_a_usuarios(self):
        self.entrar("luis@ejemplo.com")
        r = self.client.get(reverse("usuarios:inicio"))
        self.assertNotContains(r, ">Usuarios</a>")
        self.assertRedirects(self.client.get(reverse("usuarios:listado")), reverse("usuarios:inicio"))

    def test_menu_no_muestra_modulos_pendientes(self):
        self.entrar("ana@ejemplo.com")
        r = self.client.get(reverse("usuarios:inicio"))
        for texto in ("Inventario", "Movimientos", "Piezas"):
            self.assertNotContains(r, f">{texto}</a>")
