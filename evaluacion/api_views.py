from django.db.models import Count
from rest_framework import viewsets

from .models import Proyecto, Evaluador, Calificacion
from .serializer import ProyectoSerializer, EvaluadorSerializer, CalificacionSerializer

class ProyectoViewSet(viewsets.ModelViewSet):
    queryset = Proyecto.objects.all().order_by("titulo")
    serializer_class = ProyectoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        titulo = self.request.query_params.get("titulo")
        equipo = self.request.query_params.get("equipo")
        categoria = self.request.query_params.get("categoria")
        evaluador = self.request.query_params.get("evaluador")

        # filtros de busqueda para proyectos
        if titulo:
            queryset = queryset.filter(titulo__icontains=titulo)
        if equipo:
            queryset = queryset.filter(equipo__icontains=equipo)
        if categoria:
            queryset = queryset.filter(categoria=categoria.upper())
        if evaluador:
            queryset = queryset.filter(evaluadores__id=evaluador)

        return queryset.distinct()


class EvaluadorViewSet(viewsets.ModelViewSet):
    queryset = Evaluador.objects.all().order_by("nombre")
    serializer_class = EvaluadorSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        nombre = self.request.query_params.get("nombre")
        correo = self.request.query_params.get("correo")

        # filtros de busqueda para evaluadores
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        if correo:
            queryset = queryset.filter(correo__icontains=correo)

        return queryset


class CalificacionViewSet(viewsets.ModelViewSet):
    queryset = Calificacion.objects.select_related(
        "proyecto", "evaluador"
    ).all().order_by("-fecha")
    serializer_class = CalificacionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        proyecto = self.request.query_params.get("proyecto")
        evaluador = self.request.query_params.get("evaluador")
        puntaje_min = self.request.query_params.get("puntaje_min")
        puntaje_max = self.request.query_params.get("puntaje_max")

        # filtros de busqueda para calificaciones
        if proyecto:
            queryset = queryset.filter(proyecto_id=proyecto)
        if evaluador:
            queryset = queryset.filter(evaluador_id=evaluador)
        if puntaje_min:
            queryset = queryset.filter(puntaje__gte=puntaje_min)
        if puntaje_max:
            queryset = queryset.filter(puntaje__lte=puntaje_max)

        return queryset