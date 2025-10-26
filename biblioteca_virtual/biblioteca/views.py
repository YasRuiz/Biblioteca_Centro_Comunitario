from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from datetime import timedelta
import uuid

from .models import Usuario, Libro, Prestamo, Reserva
from .forms import LoginForm, LibroForm, CrearUsuarioForm, EditarUsuarioForm

# ---------------------------------------
# Home
# ---------------------------------------
def home(request):
    return render(request, 'biblioteca/home.html')


# ---------------------------------------
# Login según tipo de usuario
# ---------------------------------------
def login_usuario(request, tipo_usuario=None):
    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)

        if user:
            if tipo_usuario and user.rol != tipo_usuario:
                messages.error(request, f"El usuario no tiene el rol de {tipo_usuario.title()}.")
            else:
                login(request, user)
                return redirect({
                    'alumno': 'dashboard_alumno',
                    'profesor': 'dashboard_profesor',
                    'bibliotecario': 'dashboard_bibliotecario',
                    'administrador': 'admin_dashboard'
                }.get(user.rol, 'home'))
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, 'biblioteca/login.html', {'form': form, 'tipo_usuario': tipo_usuario})


# ---------------------------------------
# Logout
# ---------------------------------------
def logout_usuario(request):
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect('home')


# ---------------------------------------
# Dashboards según rol
# ---------------------------------------
@login_required
def dashboard_bibliotecario(request):
    if request.user.rol != 'bibliotecario':
        messages.warning(request, "No tienes permiso para acceder a esta página.")
        return redirect('home')

    context = {
        'libros_disponibles': Libro.objects.filter(disponible=True),
        'libros_prestados': Libro.objects.filter(disponible=False),
        'prestamos': Prestamo.objects.all(),
        'morosos': [p for p in Prestamo.objects.all() if p.dias_mora() > 0],
        'usuarios': Usuario.objects.filter(rol__in=['alumno', 'profesor'])
    }
    return render(request, 'biblioteca/dashboard_bibliotecario.html', context)


@login_required
def dashboard_alumno(request):
    if request.user.rol != 'alumno':
        messages.warning(request, "No tienes permiso para acceder a esta página.")
        return redirect('home')

    context = {
        'libros_disponibles': Libro.objects.filter(disponible=True),
        'reservas_usuario': Reserva.objects.filter(usuario=request.user),
        'prestamos_usuario': Prestamo.objects.filter(usuario=request.user),
    }
    return render(request, 'biblioteca/dashboard_alumno.html', context)


@login_required
def dashboard_profesor(request):
    if request.user.rol != 'profesor':
        messages.warning(request, "No tienes permiso para acceder a esta página.")
        return redirect('home')

    context = {
        'libros_disponibles': Libro.objects.filter(disponible=True),
        'reservas_usuario': Reserva.objects.filter(usuario=request.user),
        'prestamos_usuario': Prestamo.objects.filter(usuario=request.user),
    }
    return render(request, 'biblioteca/dashboard_profesor.html', context)


# ---------------------------------------
# Funciones de usuario
# ---------------------------------------
@login_required
@require_POST
def reservar_libro(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    if not libro.disponible:
        Reserva.objects.create(usuario=request.user, libro=libro)
        messages.success(request, f"Has reservado el libro '{libro.titulo}'")
    else:
        messages.warning(request, f"El libro '{libro.titulo}' está disponible, no es necesario reservar")

    return redirect({
        'alumno': 'dashboard_alumno',
        'profesor': 'dashboard_profesor',
    }.get(request.user.rol, 'dashboard_bibliotecario'))


@login_required
def renovar_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id, usuario=request.user)
    if not prestamo.renovado:
        prestamo.fecha_devolucion += timedelta(days=7)
        prestamo.renovado = True
        prestamo.save()
        messages.success(request, f"Préstamo del libro '{prestamo.libro.titulo}' renovado 7 días más")
    else:
        messages.warning(request, "Este préstamo ya fue renovado una vez")

    return redirect({
        'alumno': 'dashboard_alumno',
        'profesor': 'dashboard_profesor',
    }.get(request.user.rol, 'dashboard_bibliotecario'))


@login_required
def pagar_multa(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    if prestamo.dias_mora() > 0:
        codigo_pago = str(uuid.uuid4()).split('-')[0].upper()
        prestamo.multa_generada = True
        prestamo.save()
        messages.success(
            request,
            f"Código de pago para '{prestamo.usuario.username}': {codigo_pago} - Monto: {prestamo.monto_multa()} pesos"
        )
    else:
        messages.warning(request, "Este préstamo no tiene multa")
    return redirect('dashboard_bibliotecario')


# ---------------------------------------
# Panel de administrador unificado
# ---------------------------------------
@login_required
def admin_dashboard(request, section=None):
    if request.user.rol != 'administrador':
        messages.warning(request, "No tienes permiso para acceder a esta página.")
        return redirect('home')

    active_section = section or 'dashboard'
    context = {
        'active_section': active_section,
        'menu_items': [
            ('dashboard', 'bi-speedometer2', 'Dashboard'),
            ('usuarios', 'bi-people', 'Usuarios'),
            ('libros', 'bi-book', 'Libros'),
            ('prestamos', 'bi-journal-check', 'Préstamos'),
            ('reservas', 'bi-bookmark-check', 'Reservas'),
        ],
        'stats_items': [
            ('Usuarios', Usuario.objects.count(), 'primary'),
            ('Libros', Libro.objects.count(), 'success'),
            ('Préstamos', Prestamo.objects.count(), 'warning'),
            ('Reservas', Reserva.objects.count(), 'danger'),
        ]
    }

    # Sección de usuarios
    if active_section == 'usuarios':
        usuarios = Usuario.objects.all()
        context['usuarios'] = usuarios

        # Crear usuario (ahora con rol editable)
        if request.method == 'POST' and 'crear_usuario' in request.POST:
            form = CrearUsuarioForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Usuario agregado correctamente")
                return redirect('admin_dashboard_section', section='usuarios')
            else:
                messages.error(request, "Error al crear usuario. Revise los datos.")

        # Editar usuario
        elif request.method == 'POST' and 'editar_usuario' in request.POST:
            user_id = request.POST.get('user_id')
            usuario = get_object_or_404(Usuario, id=user_id)
            form = EditarUsuarioForm(request.POST, instance=usuario)
            if form.is_valid():
                form.save()
                messages.success(request, "Usuario actualizado correctamente")
                return redirect('admin_dashboard_section', section='usuarios')
            else:
                messages.error(request, "Error al actualizar usuario. Revise los datos.")
        else:
            form = CrearUsuarioForm()

        context['form'] = form

    # Sección de libros
    elif active_section == 'libros':
        context['libros'] = Libro.objects.all()
        form = LibroForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            form.save()
            messages.success(request, "Libro agregado correctamente")
            return redirect('admin_dashboard_section', section='libros')
        context['form'] = form

    # Sección de préstamos
    elif active_section == 'prestamos':
        context['prestamos'] = Prestamo.objects.all()

    # Sección de reservas
    elif active_section == 'reservas':
        context['reservas'] = Reserva.objects.all()

    # Dashboard principal
    else:
        context.update({
            'usuarios': Usuario.objects.all(),
            'libros': Libro.objects.all(),
            'prestamos': Prestamo.objects.all(),
            'reservas': Reserva.objects.all(),
        })

    return render(request, 'biblioteca/admin.html', context)


# Eliminar usuario
@login_required
def eliminar_usuario(request, id):
    if request.user.rol != 'administrador':
        messages.warning(request, "No tienes permiso para realizar esta acción.")
        return redirect('home')

    usuario = get_object_or_404(Usuario, id=id)

    if usuario.rol == 'administrador':
        messages.error(request, "No puedes eliminar a otro administrador.")
    else:
        usuario.delete()
        messages.success(request, f"Usuario '{usuario.username}' eliminado correctamente.")

    return redirect('admin_dashboard_section', section='usuarios')
