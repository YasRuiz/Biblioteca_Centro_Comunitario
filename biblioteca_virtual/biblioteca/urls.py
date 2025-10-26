from django.urls import path
from . import views

urlpatterns = [
    # -----------------------------
    # Home y login
    # -----------------------------
    path('', views.home, name='home'),
    path('login/', views.login_usuario, name='login'),  # login genérico
    path('login/<str:tipo_usuario>/', views.login_usuario, name='login_rol'),  # login por rol opcional
    path('logout/', views.logout_usuario, name='logout_usuario'),  # <-- logout agregado

    # -----------------------------
    # Dashboards por tipo de usuario
    # -----------------------------
    path('bibliotecario/dashboard/', views.dashboard_bibliotecario, name='dashboard_bibliotecario'),
    path('alumno/dashboard/', views.dashboard_alumno, name='dashboard_alumno'),
    path('profesor/dashboard/', views.dashboard_profesor, name='dashboard_profesor'),

    # -----------------------------
    # Funciones de usuario
    # -----------------------------
    path('libro/reservar/<int:libro_id>/', views.reservar_libro, name='reservar_libro'),
    path('prestamo/renovar/<int:prestamo_id>/', views.renovar_prestamo, name='renovar_prestamo'),

    # -----------------------------
    # Función de bibliotecario para pagar multa
    # -----------------------------
    path('multa/pagar/<int:prestamo_id>/', views.pagar_multa, name='pagar_multa'),

    # -----------------------------
    # Panel administrador
    # -----------------------------
    path('panel/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/<str:section>/', views.admin_dashboard, name='admin_dashboard_section'),

    # -----------------------------
    # Gestión de usuarios (eliminar)
    # -----------------------------
    path('panel/usuarios/eliminar/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),
]
