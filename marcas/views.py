from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.decorators import login_requerido, solo_administrador

from .models import Marca

POR_PAGINA = 25


@login_requerido
def listado(request):
    q = request.GET.get("q", "").strip()
    marcas = Marca.objects.all()
    if q:
        marcas = marcas.filter(nombre__icontains=q)

    pagina = Paginator(marcas, POR_PAGINA).get_page(request.GET.get("page"))
    contexto = {
        "seccion": "marcas",
        "pagina": pagina,
        "q": q,
        "total_registradas": Marca.objects.count(),
        "por_pagina": POR_PAGINA,
    }
    return render(request, "marcas/listado.html", contexto)


@solo_administrador
def nueva(request):
    nombre = ""
    error = None

    if request.method == "POST":
        nombre = " ".join(request.POST.get("nombre", "").split())  # quita espacios sobrantes
        if not nombre:
            error = "Completa el campo para continuar."
        elif len(nombre) > 100:
            error = "El nombre no puede superar los 100 caracteres."
        elif Marca.objects.filter(nombre__iexact=nombre).exists():
            error = "Esa marca ya está registrada."
        else:
            Marca.objects.create(nombre=nombre)
            messages.success(request, f"Marca «{nombre}» guardada.")
            return redirect("marcas:listado")

    return render(request, "marcas/nueva.html", {"seccion": "marcas", "nombre": nombre, "error": error})


@solo_administrador
def eliminar(request, id_marca):
    marca = get_object_or_404(Marca, pk=id_marca)
    total = marca.total_piezas()

    if request.method == "POST":
        if total:
            messages.error(request, f"No se puede eliminar «{marca.nombre}»: tiene piezas asociadas.")
        else:
            marca.delete()
            messages.success(request, f"Marca «{marca.nombre}» eliminada.")
        return redirect("marcas:listado")

    return render(request, "marcas/eliminar.html", {"seccion": "marcas", "marca": marca, "total": total})
