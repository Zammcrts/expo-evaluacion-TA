from django.contrib import admin
from .models import Proyecto, Evaluador, Calificacion
# Register your models here.
class CalificacionInline(admin.TabularInline):
    model = Calificacion
    extra = 0

@admin.register(Proyecto)

class ProyectoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'equipo', 'categoria']
    list_filter = ['categoria']
    inlines = [CalificacionInline]

admin.site.register(Evaluador)
admin.site.register(Calificacion)