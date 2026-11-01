from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

from usuarios.models import Usuario
from usuarios.tests import CLAVE, crear_usuario

from .models import Marca


def entrar(cliente, correo):
    cliente.post(reverse("usuarios:login"), {"correo": correo, "contrasena": CLAVE})


class MarcasVistasTests(TestCase):
    def setUp(self):
        crear_usuario("ana@ejemplo.com", "administrador")
        crear_usuario("luis@ejemplo.com", "empleado", "Luis Martínez")
        self.admin = Client()
        entrar(self.admin, "ana@ejemplo.com")
        self.empleado = Client()
        entrar(self.empleado, "luis@ejemplo.com")

    def test_admin_crea_marca_y_la_ve_en_el_listado(self):
        r = self.admin.post(reverse("marcas:nueva"), {"nombre": "  Mazda  "})
        self.assertRedirects(r, reverse("marcas:listado"))
        self.assertTrue(Marca.objects.filter(nombre="Mazda").exists())
        self.assertContains(self.admin.get(reverse("marcas:listado")), "Mazda")

    def test_no_permite_duplicados_ni_vacios(self):
        Marca.objects.create(nombre="Ford")
        r = self.admin.post(reverse("marcas:nueva"), {"nombre": "ford"})
        self.assertContains(r, "Esa marca ya está registrada.")
        r = self.admin.post(reverse("marcas:nueva"), {"nombre": "   "})
        self.assertContains(r, "Completa el campo para continuar.")
        self.assertEqual(Marca.objects.count(), 1)

    def test_eliminar_pide_confirmacion_y_borra_por_post(self):
        marca = Marca.objects.create(nombre="Mazda")
        url = reverse("marcas:eliminar", args=[marca.id_marca])
        self.assertContains(self.admin.get(url), "¿Eliminar la marca Mazda?")
        self.assertTrue(Marca.objects.filter(pk=marca.pk).exists())  # el GET no borra
        self.admin.post(url)
        self.assertFalse(Marca.objects.filter(pk=marca.pk).exists())

    def test_no_se_elimina_una_marca_con_piezas(self):
        marca = Marca.objects.create(nombre="Nissan")
        url = reverse("marcas:eliminar", args=[marca.id_marca])
        with patch.object(Marca, "total_piezas", return_value=4):
            self.assertContains(self.admin.get(url), "No se puede eliminar")
            self.admin.post(url)
        self.assertTrue(Marca.objects.filter(pk=marca.pk).exists())

    def test_empleado_consulta_pero_no_crea_ni_elimina(self):
        marca = Marca.objects.create(nombre="Toyota")
        r = self.empleado.get(reverse("marcas:listado"))
        self.assertContains(r, "Toyota")
        self.assertNotContains(r, "Nueva marca")
        self.assertNotContains(r, "Eliminar")
        self.assertRedirects(self.empleado.post(reverse("marcas:nueva"), {"nombre": "X"}), reverse("usuarios:inicio"))
        self.empleado.post(reverse("marcas:eliminar", args=[marca.id_marca]))
        self.assertTrue(Marca.objects.filter(pk=marca.pk).exists())
        self.assertFalse(Marca.objects.filter(nombre="X").exists())

    def test_busqueda_y_paginacion(self):
        for i in range(30):
            Marca.objects.create(nombre=f"Marca {i:02d}")
        r = self.admin.get(reverse("marcas:listado"))
        self.assertEqual(len(r.context["pagina"]), 25)
        r = self.admin.get(reverse("marcas:listado"), {"page": 2})
        self.assertEqual(len(r.context["pagina"]), 5)
        r = self.admin.get(reverse("marcas:listado"), {"q": "Marca 07"})
        self.assertEqual(r.context["pagina"].paginator.count, 1)


class MarcasApiTests(TestCase):
    def setUp(self):
        crear_usuario("ana@ejemplo.com", "administrador")
        crear_usuario("luis@ejemplo.com", "empleado", "Luis Martínez")
        self.url = "/api/marcas/"

    def cliente(self, correo=None):
        c = Client(enforce_csrf_checks=True)
        c.get(reverse("usuarios:login"))  
        if correo:
            token = c.cookies["csrftoken"].value
            c.post(reverse("usuarios:login"), {"correo": correo, "contrasena": CLAVE, "csrfmiddlewaretoken": token})
        return c

    def cabecera(self, c):
        return {"HTTP_X_CSRFTOKEN": c.cookies["csrftoken"].value}

    def test_sin_sesion_no_hay_acceso(self):
        self.assertEqual(self.cliente().get(self.url).status_code, 403)

    def test_admin_crud_completo(self):
        c = self.cliente("ana@ejemplo.com")
        h = self.cabecera(c)
        r = c.post(self.url, {"nombre": "Mazda"}, content_type="application/json", **h)
        self.assertEqual(r.status_code, 201)
        id_marca = r.json()["id_marca"]
        self.assertEqual(r.json()["piezas_asociadas"], 0)
        self.assertEqual(c.get(self.url).status_code, 200)
        r = c.patch(f"{self.url}{id_marca}/", {"nombre": "Mazda MX"}, content_type="application/json", **h)
        self.assertEqual(r.status_code, 200)
        r = c.post(self.url, {"nombre": "mazda mx"}, content_type="application/json", **h)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(c.delete(f"{self.url}{id_marca}/", **h).status_code, 204)

    def test_escritura_sin_csrf_se_rechaza(self):
        c = self.cliente("ana@ejemplo.com")
        r = c.post(self.url, {"nombre": "Mazda"}, content_type="application/json")
        self.assertEqual(r.status_code, 403)
        self.assertEqual(Marca.objects.count(), 0)

    def test_empleado_solo_lee(self):
        c = self.cliente("luis@ejemplo.com")
        self.assertEqual(c.get(self.url).status_code, 200)
        r = c.post(self.url, {"nombre": "Mazda"}, content_type="application/json", **self.cabecera(c))
        self.assertEqual(r.status_code, 403)

    def test_no_borra_marca_con_piezas(self):
        marca = Marca.objects.create(nombre="Nissan")
        c = self.cliente("ana@ejemplo.com")
        with patch.object(Marca, "total_piezas", return_value=2):
            r = c.delete(f"{self.url}{marca.id_marca}/", **self.cabecera(c))
        self.assertEqual(r.status_code, 409)
        self.assertTrue(Marca.objects.filter(pk=marca.pk).exists())
