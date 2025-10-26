from django.contrib import admin
from .models import Usuario, Libro, Prestamo, Reserva
from django.contrib.auth.admin import UserAdmin

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Rol', {'fields': ('rol',)}),
    )
    list_display = ('username', 'rol', 'is_active', 'is_staff')

admin.site.register(Libro)
admin.site.register(Prestamo)
admin.site.register(Reserva)
