
from rest_framework import serializers
from .models import Proyecto, Evaluador, Calificacion


class EvaluadorResumenSerializer(serializers.ModelSerializer):
    # para mostrar info breve de los evaluadores en el detalle de un proyecto
    class Meta:
        model = Evaluador
        fields = ['id', 'nombre']


class ProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = ['id', 'titulo', 'equipo', 'categoria', 'evaluadores']


class EvaluadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluador
        fields = ['id', 'nombre', 'correo']


class CalificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calificacion
        fields = [
            'id',
            'proyecto',
            'evaluador',
            'puntaje',
            'comentario',
            'fecha'
        ]
        read_only_fields = ['fecha']