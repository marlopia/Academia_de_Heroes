from django.http import HttpResponse
from django.shortcuts import redirect, render

from app.models import Personaje


# Create your views here.
def index(request):
    return HttpResponse("Hello world!")


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

        return redirect("/crear")

    return render(request, "crear.html")


def listar(request):
    return HttpResponse(Personaje.objects.all())
