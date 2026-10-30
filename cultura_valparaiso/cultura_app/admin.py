from django.contrib import admin
from .models import Etiqueta, Evento, Usuario


class ActivacionAdminMixin:
    list_display = ('__str__', 'activo')
    list_editable = ('activo',)
    list_filter = ('activo',)
    actions = ('activar_seleccionados', 'desactivar_seleccionados')

    @admin.action(description='Activar elementos seleccionados')
    def activar_seleccionados(self, request, queryset):
        actualizados = queryset.update(activo=True)
        self.message_user(request, f'{actualizados} elemento(s) activado(s).')

    @admin.action(description='Desactivar elementos seleccionados')
    def desactivar_seleccionados(self, request, queryset):
        actualizados = queryset.update(activo=False)
        self.message_user(request, f'{actualizados} elemento(s) desactivado(s).')

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Evento)
class EventoAdmin(ActivacionAdminMixin, admin.ModelAdmin):
    list_display = ('nombre', 'fecha', 'direccion', 'activo')
    search_fields = ('nombre', 'direccion', 'descripcion')
    filter_horizontal = ('etiquetas',)


@admin.register(Usuario)
class UsuarioAdmin(ActivacionAdminMixin, admin.ModelAdmin):
    list_display = ('nombre', 'distancia_maxima', 'activo')
    search_fields = ('nombre',)
    filter_horizontal = ('gustos',)


@admin.register(Etiqueta)
class EtiquetaAdmin(ActivacionAdminMixin, admin.ModelAdmin):
    search_fields = ('nombre',)
