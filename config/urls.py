
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(pattern_name="usuarios:login", permanent=False)),
    path("usuarios/", include("usuarios.urls")),


    path("marcas/", include("marcas.urls")),
    path("api/marcas/", include("marcas.api_urls")),         # API REST de marcas
    # path("piezas/", include("piezas.urls")),                 #  piezas
    # path("inventario/", include("inventario.urls")),         #  inventario
    # path("movimientos/", include("movimientos.urls")),       #  movimientos
]
