from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from app.models import Arquero, Guerrero, Mago, Personaje, Perfil


# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return redirect("user_login")
    return render(request, "index.html")


def crear(request):

    if request.method == "POST":

        nombre = request.POST.get("nombre")
        nivel = request.POST.get("nivel")
        vida = request.POST.get("vida")
        clase = request.POST.get("clase")

        if clase == "guerrero":
            armadura = request.POST.get("armadura")
            Guerrero.objects.create(
                nombre=nombre, nivel=int(nivel), vida=int(vida), armadura=int(armadura), usuario=request.user.id
                )
            messages.success(request, "Personaje creado correctamente")
            return redirect("/crear")

        elif clase == "mago":
            mana = request.POST.get("mana")
            Mago.objects.create(
                nombre=nombre, nivel=int(nivel), vida=int(vida), mana=int(mana), usuario=request.user.id
                )
            messages.success(request, "Personaje creado correctamente")
            return redirect("/crear")

        elif clase == "arquero":
            precision = request.POST.get("precision")
            Arquero.objects.create(
                nombre=nombre, nivel=int(nivel), vida=int(vida), precision=int(precision), usuario=request.user.id
                )
            messages.success(request, "Personaje creado correctamente")
            return redirect("/crear")

        else:
            messages.error(request, "Error: Clase no reconocida")
            return redirect("/crear")

    return render(request, "crear.html")


def buscar(request):
    personajes = Personaje.objects.filter(usuario=request.user.id)

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


def buscar_personajes(request):
    nombre = request.GET.get("nombre", "")
    nivel = request.GET.get("nivel", "")
    vida = request.GET.get("vida", "")
    clase = request.GET.get("clase", "")

    personajes = Personaje.objects.filter(usuario=request.user.id)

    if nombre:
        personajes = personajes.filter(nombre__icontains=nombre)

    if nivel:
        personajes = personajes.filter(nivel=nivel)

    if vida:
        personajes = personajes.filter(vida__gte=vida)

    if clase == "guerrero":
        personajes = personajes.filter(guerrero__isnull=False)

    elif clase == "mago":
        personajes = personajes.filter(mago__isnull=False)

    elif clase == "arquero":
        personajes = personajes.filter(arquero__isnull=False)

    data = []

    for p in personajes:
        if hasattr(p, "guerrero"):
            clase_nombre = "Guerrero"
        elif hasattr(p, "mago"):
            clase_nombre = "Mago"
        elif hasattr(p, "arquero"):
            clase_nombre = "Arquero"
        else:
            clase_nombre = "Desconocido"

        data.append({
            "id": p.id,
            "nombre": p.nombre,
            "nivel": p.nivel,
            "vida": p.vida,
            "vida_max": p.vida_max,
            "clase": clase_nombre,
        })

    return JsonResponse(data, safe=False)


def user_login(request):
    if request.method == "POST":
        usuario = request.POST.get("user", "")
        password = request.POST.get("password", "")

        user = authenticate(request, username=usuario, password=password)

        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "Credenciales incorrectas")
            return redirect("user_login")

    return render(request, "login.html")


def registrar(request):
    if request.method == "POST":
        usuario = request.POST.get("user", "")
        dni = request.POST.get("dni", "")
        telefono = request.POST.get("telefono", "")
        fnac = request.POST.get("fnac", "")
        password = request.POST.get("password", "")

        user = User.objects.create_user(username=usuario, password=password)

        Perfil.objects.create(user=user, dni=dni, telefono=telefono, fnac=fnac)

        messages.success(request, "Usuario registrado!")

        return redirect("user_login")

    return render(request, "register.html")


def user_logout(request):
    logout(request)
    return redirect("user_login")


def comprar_mercenario(request):
    if request.method == "POST":
        perfil = request.user.perfil

        if perfil.monedas >= 3:
            perfil.monedas -= 3
            perfil.mercenarios += 1
            perfil.save()
        else:
            messages.error(request, "Monedas insuficientes")

    return redirect(request.META.get("HTTP_REFERER", "/"))


def entrenar(request, id):
    if request.method == "POST":
        perfil = request.user.perfil
        personaje = get_object_or_404(Personaje, id=id)

        if perfil.mercenarios >= 1:
            perfil.mercenarios -= 1
            personaje.subir_nivel()

            perfil.save()
        else:
            messages.error(request, "No tienes mercenarios")

    return redirect(request.META.get("HTTP_REFERER", "/"))
