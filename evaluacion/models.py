from django.db import models
from django.db.models import Q

class Proyecto(models.Model):
    class Categoria(models.TextChoices):
        SOFTWARE = "SW", "Software"
        HARDWARE = "HW", "Hardware"
        IA = "IA", "Inteligencia Artificial"
        SOCIAL = "SC", "Impacto social"

    titulo = models.CharField(max_length=200)
    equipo = models.CharField(max_length=200)
    categoria = models.CharField(max_length=2, choices=Categoria.choices)
    evaluadores = models.ManyToManyField(
        "Evaluador", through="Calificacion", related_name="proyectos")

    def __str__(self):
        return self.titulo

class Evaluador(models.Model):
    nombre = models.CharField(max_length=200)
    correo = models.EmailField(unique=True)

    def __str__(self):
        return self.nombre

class Calificacion(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="calificaciones")
    evaluador = models.ForeignKey(Evaluador, on_delete=models.CASCADE, related_name="calificaciones")
    puntaje = models.DecimalField(max_digits=4, decimal_places=2)
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['proyecto', 'evaluador'],
                name='una_calificacion_por_evaluador'
            ),
            models.CheckConstraint(
                condition=Q(puntaje__gte=0) & Q(puntaje__lte=10),
                name='puntaje_valido'
            ),
        ]