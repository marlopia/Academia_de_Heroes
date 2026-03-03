"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("crear/", views.crear, name="crear"),
    path("buscar/", views.buscar, name="buscar"),
    path("luchar/", views.luchar, name="luchar"),
    path("<int:id>/info/", views.info_personaje, name="info_personaje"),
    path("favicon.ico", RedirectView.as_view(url="/static/app/images/favicon.ico")),
    path("buscar/api/", views.buscar_personajes, name="buscar_api"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
