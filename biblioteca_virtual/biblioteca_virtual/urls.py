from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('biblioteca.urls')),

    # Login y logout usando vistas de Django
    path('login/', auth_views.LoginView.as_view(template_name='biblioteca/login.html'), name='login_general'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]
