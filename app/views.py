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
    return render(request, "luchar.html")


def info_personaje(request, id):
    personaje = get_object_or_404(Personaje, id=id)
    return render(request, "info.html", {"personaje": personaje})
