from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from app.models import Personaje


# Create your views here.
def index(request):
    return render(request, "index.html")


def crear(request):

    if request.method == "POST":

        nombre = request.POST.get("nombre")
        nivel = request.POST.get("nivel")
        vida = request.POST.get("vida")

        Personaje.objects.create(
            nombre=nombre,
            nivel=int(nivel),
            vida=int(vida),
        )

        messages.success(request, "Personaje creado correctamente")
        return redirect("/crear")

    return render(request, "crear.html")


def buscar(request):
    personajes = Personaje.objects.all()

    return render(request, "buscar.html", {"personajes": personajes})


def luchar(request):
    personajes = Personaje.objects.all()

    if request.method == "POST":
        personaje_id1 = request.POST.get("personaje1")
        personaje1 = Personaje.objects.get(id=personaje_id1)

        personaje_id2 = request.POST.get("personaje2")
        personaje2 = Personaje.objects.get(id=personaje_id2)

        return render(
            request,
            "luchar.html",
            {
                "personajes": personajes,
                "seleccionado1": personaje1,
                "seleccionado2": personaje2,
            },
        )

    return render(request, "luchar.html", {"personajes": personajes})


def info_personaje(request, id):
    personaje = get_object_or_404(Personaje, id=id)

    if request.method == "POST":
        if "guardar" in request.POST:
            personaje.nombre = request.POST.get("nombre", personaje.nombre)
            personaje.nivel = int(request.POST.get("nivel", personaje.nivel))
            personaje.vida = int(request.POST.get("vida", personaje.vida))
            personaje.vida_max = int(request.POST.get("vida_max", personaje.vida_max))
            personaje.save()
            messages.success(request, "Personaje actualizado correctamente")
            return redirect("info_personaje", id=id)

        elif "borrar" in request.POST:
            personaje.delete()
            messages.success(request, "Personaje borrado correctamente")
            return redirect("buscar")

    return render(request, "info.html", {"personaje": personaje})
