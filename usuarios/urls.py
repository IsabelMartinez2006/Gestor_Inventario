from django.urls import path

from . import views

app_name = "usuarios"

urlpatterns = [
    path("", views.listado, name="listado"),
    path("inicio/", views.inicio, name="inicio"),
    path("login/", views.login_vista, name="login"),
    path("logout/", views.logout_vista, name="logout"),
]
