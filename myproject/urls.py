"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from comedor_django.views import opciones,menu,nueva_clave,registrar_usuario,turnos,mi_turno, api_turnos,procesar_solicitud,api_login, api_mostrar_solicitud, api_liberar_reserva, api_registrar_usuario,api_recuperar_clave, api_validar_codigo, api_cambiar_clave, login, recuperar_clave

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/turnos/', api_turnos, name='api_turnos'),
    path('api/login/', api_login, name='api_login'),
    path('procesar-solicitud/', procesar_solicitud, name='procesar_solicitud'),
    path('api/mostrar-solicitud/<int:id_usuario>/', api_mostrar_solicitud, name='api_mostrar_solicitud'),
    path('api/liberar-reserva/', api_liberar_reserva, name='api_liberar_reserva'),
    path('api/registrar-usuario/', api_registrar_usuario, name='api_registrar_usuario'),
    path('api/recuperar-clave/', api_recuperar_clave, name='api_recuperar_clave'),
    path('api/validar-codigo/', api_validar_codigo, name='api_validar_codigo'),
    path('api/cambiar-clave/', api_cambiar_clave, name='api_cambiar_clave'),
    
    path('login/', login, name='login'),
    path('recuperar-clave/', recuperar_clave, name='recuperar_clave'),
    path('registrar-usuario/', registrar_usuario, name='registrar_usuario'),
    path('turnos/', turnos, name='turnos'),
    path('mi-turno/', mi_turno, name='mi_turno'),
    path('nueva-clave/', nueva_clave, name='nueva_clave'),
    path('menu/', menu, name='menu'),
    path('opciones/', opciones, name='opciones'),
        
    
]
