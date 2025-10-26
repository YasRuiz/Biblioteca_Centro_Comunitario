from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

# ---------------------------------------------------------
# Usuario personalizado con roles
# ---------------------------------------------------------
class Usuario(AbstractUser):
    ROLES = (
        ('administrador', 'Administrador'),
        ('bibliotecario', 'Bibliotecario'),
        ('profesor', 'Profesor'),
        ('alumno', 'Alumno'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='alumno')

    def save(self, *args, **kwargs):
        # Asegurar que los bibliotecarios sean staff para admin
        if self.rol == 'bibliotecario':
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"


# ---------------------------------------------------------
# Libro
# ---------------------------------------------------------
class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    isbn = models.CharField(max_length=20, unique=True)
    disponible = models.BooleanField(default=True)
    fecha_publicacion = models.DateField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.titulo} - {self.autor}"


# ---------------------------------------------------------
# Préstamo
# ---------------------------------------------------------
class Prestamo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    fecha_prestamo = models.DateField(auto_now_add=True)
    fecha_devolucion = models.DateField(blank=True, null=True)
    renovado = models.BooleanField(default=False)
    devuelto = models.BooleanField(default=False)
    multa_generada = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Asignar fecha de devolución si no existe
        if not self.fecha_devolucion:
            self.fecha_devolucion = self.fecha_prestamo + timedelta(days=7)
        super().save(*args, **kwargs)

    def dias_mora(self):
        if not self.devuelto:
            hoy = timezone.now().date()
            dias = (hoy - self.fecha_devolucion).days
            return dias if dias > 0 else 0
        return 0

    def monto_multa(self):
        return self.dias_mora() * 100  # 100 pesos por día de retraso

    def __str__(self):
        estado = "Devuelto" if self.devuelto else "Pendiente"
        return f"{self.usuario} - {self.libro} ({estado})"


# ---------------------------------------------------------
# Reserva
# ---------------------------------------------------------
class Reserva(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    fecha_reserva = models.DateField(auto_now_add=True)
    atendida = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.usuario} reservó {self.libro}"


# ---------------------------------------------------------
# Configuración del sistema
# ---------------------------------------------------------
class Configuracion(models.Model):
    nombre = models.CharField(max_length=100)
    valor = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.nombre}: {self.valor}"
