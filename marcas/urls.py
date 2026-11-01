from django.urls import path

from . import views

app_name = "marcas"

urlpatterns = [
    path("", views.listado, name="listado"),
    path("nueva/", views.nueva, name="nueva"),
    path("<int:id_marca>/eliminar/", views.eliminar, name="eliminar"),
]
