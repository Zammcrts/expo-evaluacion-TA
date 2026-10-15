from django.db.models import Count
from rest_framework import viewsets
from django.db.models import Avg, Count, Max, Min
from rest_framework.response import Response
from rest_framework.views import APIView

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

def redondear(valor):
    return round(float(valor), 2) if valor is not None else None


class EstadisticasView(APIView):
    def get(self, request):
        #proyectos con promedio
        proyectos = Proyecto.objects.annotate(
            promedio=Avg("calificaciones__puntaje"),
            num_calificaciones=Count("calificaciones"),
        ).filter(num_calificaciones__gt=0)

        #por categorias
        categoria = request.query_params.get("categoria")
        if categoria:
            proyectos = proyectos.filter(categoria=categoria.upper())

        #mayor a menor por defecto
        orden = "promedio" if request.query_params.get("orden") == "asc" else "-promedio"
        proyectos = proyectos.order_by(orden, "titulo")

        #limite por parametro
        limit = request.query_params.get("limit")
        if limit and limit.isdigit():
            proyectos = proyectos[:int(limit)]

        ranking = [
            {
                "posicion": i,
                "id": p.id,
                "titulo": p.titulo,
                "equipo": p.equipo,
                "categoria": p.categoria,
                "promedio": redondear(p.promedio),
                "num_calificaciones": p.num_calificaciones,
            }
            for i, p in enumerate(proyectos, start=1)
        ]

        #resumenes por cat
        nombres = dict(Proyecto.Categoria.choices)
        por_categoria = [
            {
                "categoria": f["proyecto__categoria"],
                "nombre": nombres.get(f["proyecto__categoria"]),
                "proyectos": f["proyectos"],
                "promedio": redondear(f["promedio"]),
                "mejor": redondear(f["mejor"]),
                "peor": redondear(f["peor"]),
            }
            for f in Calificacion.objects.values("proyecto__categoria")
            .annotate(
                proyectos=Count("proyecto", distinct=True),
                promedio=Avg("puntaje"),
                mejor=Max("puntaje"),
                peor=Min("puntaje"),
            )
            .order_by("-promedio")
        ]

        #gerenales
        agg = Calificacion.objects.aggregate(promedio=Avg("puntaje"))
        general = {
            "total_proyectos": Proyecto.objects.count(),
            "total_evaluadores": Evaluador.objects.count(),
            "total_calificaciones": Calificacion.objects.count(),
            "promedio_general": redondear(agg["promedio"]),
        }

        return Response({
            "general": general,
            "por_categoria": por_categoria,
            "ranking": ranking,
        })