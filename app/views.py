from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from plotly.offline import plot
import plotly.graph_objs as go
from django.shortcuts import get_object_or_404, redirect, render

from app.models import Arquero, Guerrero, Mago, Personaje

ATRIBUTOS_EXTRA = {
    "Guerrero": "armadura",
    "Mago": "mana",
    "Arquero": "precision",
}


# Create your views here.
def index(request):
    conteos = {
        "Guerrero": Guerrero.objects.count(),
        "Arquero": Arquero.objects.count(),
        "Mago": Mago.objects.count(),
    }

    fig = go.Figure(
        data=[
            go.Bar(
                x=list(conteos.keys()),
                y=list(conteos.values()),
                marker_color=["#4e79a7", "#e15759", "#f28e2b"],
            )
        ]
    )
    fig.update_layout(
        title="Conteo de personajes por clase",
        xaxis_title="Clase",
        yaxis_title="Cantidad",
    )

    plot_div = plot(
        fig, output_type="div", include_plotlyjs=False
    )  # Solo el div, JS externo

    return render(request, "index.html", {"plot_div": plot_div})


def crear(request):

    if request.method == "POST":

        nombre = request.POST.get("nombre")
        clase = request.POST.get("clase")
        nivel = request.POST.get("nivel")
        vida = request.POST.get("vida")

        if clase == "Guerrero":
            Guerrero.objects.create(
                nombre=nombre,
                nivel=int(nivel),
                vida=int(vida),
            )
        elif clase == "Mago":
            Mago.objects.create(
                nombre=nombre,
                nivel=int(nivel),
                vida=int(vida),
            )
        elif clase == "Arquero":
            Arquero.objects.create(
                nombre=nombre,
                nivel=int(nivel),
                vida=int(vida),
            )

        messages.success(request, "Personaje creado correctamente")
        return redirect("/crear")

    else:
        clases = [cls.__name__ for cls in Personaje.__subclasses__()]
        return render(request, "crear.html", {"clases": clases})


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
    personaje = Personaje.objects.get(id=id)
    clases = [cls.__name__ for cls in Personaje.__subclasses__()]
    clase_actual = personaje.__class__.__name__

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

        elif "entrenar" in request.POST:
            personaje.subir_nivel()
            messages.success(
                request, f"{personaje.nombre} subió a nivel {personaje.nivel}!"
            )
            return redirect("info_personaje", id=id)

    return render(
        request,
        "info.html",
        {"personaje": personaje, "clases": clases, "clase_actual": clase_actual},
    )


def buscar_personajes(request):
    nombre = request.GET.get("nombre", "")
    nivel = request.GET.get("nivel", "")
    vida = request.GET.get("vida", "")

    personajes = Personaje.objects.all()

    if nombre:
        personajes = personajes.filter(nombre__icontains=nombre)

    if nivel:
        personajes = personajes.filter(nivel=nivel)

    if vida:
        personajes = personajes.filter(vida__gte=vida)

    data = [
        {
            "id": p.id,
            "nombre": p.nombre,
            "nivel": p.nivel,
            "vida": p.vida,
            "vida_max": p.vida_max,
        }
        for p in personajes
    ]

    return JsonResponse(data, safe=False)
