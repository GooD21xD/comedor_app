from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt #, csrf_protect
from .models import Usuario, Reserva, Turno
import json
import jwt # para usar token
import secrets #generar clave aleatorio
import random
from django.core.mail import send_mail #para enviar mail de recuperacion de clave

from .tasks import reset_codigo #funcion para resetear codigo de recuperacion de clave
import threading

# Create your views here.
def registrar_usuario(request):

    context = {
        'paises': 'paises',
    }

    return render(request, 'registrar_usuario.html', context)

def turnos(request):

    context = {
        'paises': 'paises',
    }

    return render(request, 'turnos.html', context)

def mi_turno(request):

    context = {
        'paises': 'paises',
    }

    return render(request, 'mi_turno.html', context)

def login(request):
    return render(request, 'login.html')

def recuperar_clave(request):
    return render(request, 'recuperar_clave.html')

def nueva_clave(request):
    return render(request, 'nueva_clave.html')

def menu(request):
    return render(request, 'menu.html')

def opciones(request):
    return render(request, 'opciones.html')

@csrf_exempt
def api_turnos(request):
    if request.method == 'GET':
        
        # Obtenemos todos los registros de la tabla Turno con estado=1
        turnos = Turno.objects.filter(estado=1)
        # Obtener la suma de cant_turno y cant_turno_total para registros con estado=1
        suma_cant_turno = sum(turnos.values_list('cant_turno', flat=True))
        suma_cant_turno_total = sum(turnos.values_list('cant_turno_total', flat=True))

        # Comparar las sumas y actualizar el estado para id_turno == 11
        if suma_cant_turno == suma_cant_turno_total:
            try:
                turno_libre = Turno.objects.get(estado=0, id_turno=11)
                turno_libre.estado = 1
                turno_libre.save()
            except Turno.DoesNotExist:
                pass  # Manejar el caso si no existe el turno libre

        # Serializamos los datos de los turnos en un diccionario
        data = [
            {
                'id_turno': turno.id_turno,
                'turno': turno.turno,
                'hora_ini': turno.hora_ini.strftime('%H:%M:%S'),
                'hora_fin': turno.hora_fin.strftime('%H:%M:%S'),
                'cant_turno': turno.cant_turno,
                'cant_turno_total': turno.cant_turno_total,
                'estado': turno.estado,
            }
            for turno in turnos
        ]

        # Devolvemos los datos serializados en formato JSON
        return JsonResponse(data, safe=False)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def procesar_solicitud(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id_turno_str = data.get('id_turno')
        id_usuario = data.get('id_usuario')
        accion= data.get('accion')
        if id_turno_str is not None:
            try:
                id_turno = int(id_turno_str)
                # Verificar si el turno existe
                try:
                    turno = Turno.objects.get(id_turno=id_turno)
                except Turno.DoesNotExist:
                    return JsonResponse({'error': 'El turno no existe.'})

                # Verificar si el usuario ya tiene una reserva
                if Reserva.objects.filter(id_usuario=id_usuario, accion=accion).exists():
                    reserva = Reserva.objects.get(id_usuario=id_usuario, accion=accion)
                    turno_r = Turno.objects.get(id_turno=reserva.id_turno.id_turno)
                    return JsonResponse({'error': f'Ya reservaste el {turno_r.turno}. No puedes hacer otra reserva.'})
                else:
                    # Actualizar la tabla de turnos
                    if turno.cant_turno < turno.cant_turno_total:
                        turno.cant_turno += 1
                        turno.save()
                        # Obtener la suma de cant_turno y cant_turno_total
                        # suma_cantidades = Turno.objects.filter(estado=1).aggregate(suma_cant_turno=models.Sum('cant_turno'), suma_cant_turno_total=models.Sum('cant_turno_total'))
                        
                        # Crear una nueva reserva relacionada con el turno
                        reserva = Reserva.objects.create(
                            id_turno=turno,
                            id_usuario=id_usuario,
                            nombre=data.get('nombre'),
                            ape_p=data.get('ape_p'),
                            hora_ini=data.get('hora_ini'),
                            hora_fin=data.get('hora_fin'),
                            accion=data.get('accion')
                        )
                        reserva.save()
                    else:
                        return JsonResponse({'error': f'El {turno} ya no esta disponible!'})    

                    return JsonResponse({'mensaje': f'El {turno} ha sido reservado con éxito!','cerrar':'1'})
                
            except ValueError:
                return JsonResponse({'error': 'El valor de id_turno no es válido.'})

        else:
            return JsonResponse({'error': 'El campo id_turno no está presente en la solicitud.'})

    else:
        return JsonResponse({'error': 'Método no permitido'})

# Definir una clave secreta para firmar los tokens (puedes cambiarla por una más segura)
# Generar una clave segura de 64 bytes
SECRET_KEY = secrets.token_hex(32)

@csrf_exempt
def api_mostrar_solicitud(request, id_usuario):
    if request.method == 'GET':
        try:
            reserva = Reserva.objects.get(id_usuario=id_usuario)
            data = {
                'id_turno': reserva.id_turno.id_turno,  # Incluir solo el ID del turno
                'id_usuario': reserva.id_usuario,
                'nombre': reserva.nombre,
                'ape_p': reserva.ape_p,
                'hora_ini': reserva.hora_ini.strftime('%H:%M'),  # Solo la hora
                'hora_fin': reserva.hora_fin.strftime('%H:%M'),  # Solo la hora
                'accion': reserva.accion,
            }
            return JsonResponse(data)
        except Reserva.DoesNotExist:
            return JsonResponse({'error': 'La reserva no existe.'})
    else:
        return JsonResponse({'error': 'Método no permitido'})

# views.py
@csrf_exempt
def api_liberar_reserva(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id_usuario_str = data.get('id_usuario')
        id_turno_str = data.get('id_turno')
        if id_usuario_str is not None:
            id_usuario = int(id_usuario_str)
            id_turno = int(id_turno_str)
            # print(f"id_usuario: {id_usuario}, id_turno: {id_turno}")  # Imprime los valores para verificar
            try:
                # Buscar la reserva relacionada con el id_usuario
                reserva = Reserva.objects.get(id_usuario=id_usuario)
                # Obtener el id_turno asociado a la reserva
                # id_turno = reserva.id_turno
                # Obtener el turno asociado a ese id_turno en la tabla turnos
                turno = Turno.objects.filter(id_turno=id_turno).first()
                if turno is not None:
                    turno.cant_turno -= 1   
                    turno.save()    
                    reserva_menor_id = Reserva.objects.filter(id_turno=11).order_by('id').first()
                    if reserva_menor_id and id_turno!=11:
                        # Obtener la reserva actual del usuario que está liberando el turno
                        # reserva_actual = Reserva.objects.get(id_usuario=id_usuario, id_turno=id_turno)
                        # Guardar los valores de la reserva_actual en reserva_menor_id
                        reserva_menor_id.hora_ini = reserva.hora_ini
                        reserva_menor_id.hora_fin = reserva.hora_fin
                        reserva_menor_id.id_turno = reserva.id_turno
                        reserva_menor_id.save()

                        turno_11 = Turno.objects.get(id_turno=11)
                        turno_11.cant_turno -= 1   
                        turno_11.save()    

                        turno_x = Turno.objects.get(id_turno=id_turno)
                        turno_x.cant_turno += 1 
                        turno_x.save() 
                    
                    # Eliminar el registro de la tabla reserva
                    reserva.delete()
                    # if id_turno == 11 and turno.estado == 1:
                    if Turno.objects.filter(id_turno=11, estado=1).exists():
                        turno_11=Turno.objects.get(id_turno=11, estado=1)
                        if turno_11.cant_turno<1: # DEBO TOMAR EN CUENTA QUE TENGO QUE COMPARAR PROPIEDADES CON VALORES, NO CON INSTANCIAS DE UNA CLASE OSEA OBJETOS
                           #AQUI ARRIBA ESTARIA MAL POR EJEMPLO HACER LA COMPARACION ENTRE "turno_11<1", ESTO ES UNA INSTANCIA DE UNA CLASE COMPARADO CON UN VALOR     
                            turno_11.estado = 0  # Cambiar el estado cuando id_turno es 11 y el estado es 1                                 
                        turno_11.save()                    
                    # return JsonResponse({'mensaje': 'Reserva liberada con éxito'})
                    return JsonResponse({'mensaje': f'El turno {id_turno} ha sido liberado con éxito!', 'cerrar':'1'})
                else:
                    return JsonResponse({'error': 'No se encontró el turno asociado a la reserva'})
            except Reserva.DoesNotExist:
                return JsonResponse({'error': 'No se encontró la reserva'})
            except Turno.DoesNotExist:
                return JsonResponse({'error': 'No se encontró el turno asociado a la reserva'}, status=404)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Solicitud no permitida'}, status=405)


@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        usuario = data.get('usuario')
        clave = data.get('clave')

        try:
            # Buscar el usuario en la base de datos por nombre de usuario y clave
            usuario_obj = Usuario.objects.get(usuario=usuario, clave=clave)
        except Usuario.DoesNotExist:
            return JsonResponse({'error': 'Credenciales incorrectas'})

        # if Reserva.objects.filter(id_usuario=usuario_obj.id_usuario).exists():
        #     reserva='1'
        # else:
        #     reserva='0' 

        reserva=Reserva.objects.filter(id_usuario=usuario_obj.id_usuario).exists()
        session=1          
        # Crear un payload para el token con la información del usuario
        payload = {
            'usuario_id': usuario_obj.id_usuario,
            'nombre': usuario_obj.nombre,
            'ape_p': usuario_obj.ape_p,
            'ape_m': usuario_obj.ape_m,
            'reserva':reserva,
            'session':session
        }

        # Generar el token JWT con el payload y la clave secreta
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # Devolver el token como respuesta en formato JSON
        return JsonResponse({'token': token})
    
@csrf_exempt
def api_registrar_usuario(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        usuario = data.get('usuario')
        # Verificar si las claves son iguales
        if data['clave'] != data['repetir_clave']:
            return JsonResponse({'error': 'Las claves no coinciden.'})
        
        try:
            # Crear el usuario en la base de datos

            if Usuario.objects.filter(usuario= usuario).exists():
                return JsonResponse({'error': f'el usuario: {usuario} ya existe por favor ingrese otro usuario'}) 
            else:
                usuario = Usuario(
                    usuario=usuario,
                    clave=data['clave'],
                    nombre=data['nombre'],
                    ape_p=data['ape_p'],
                    ape_m=data['ape_m'],
                    fec_nac=data['fec_nac'],
                    correo=data['correo'],
                    telefono=data['telefono']
                )
                usuario.save()
                return JsonResponse({'mensaje': 'Usuario registrado exitosamente.'})
            
        except Exception as e:
            return JsonResponse({'error': 'Error al registrar el usuario.'})


@csrf_exempt
def api_recuperar_clave(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            usuario = data.get('usuario')
            contacto = data.get('contacto')  # 'telefono' o 'correo'
            telefono = data.get('telefono', '')  # Vacío si no se proporciona teléfono
            correo = data.get('correo', '')  # Vacío si no se proporciona correo

            # Verificar si el usuario existe
            user=Usuario.objects.get(usuario=usuario)
            # user = get_object_or_404(Usuario, usuario=usuario)
            id_usuario = user.id_usuario
            
            if contacto == 'telefono':
                # Procesar la recuperación usando el teléfono
                if user.telefono == telefono:
                    # Aquí puedes enviar el mensaje de recuperación por teléfono
                    return JsonResponse({'mensaje': 'esta funcion esta en desarrollo.'})
                else:
                   return JsonResponse({'error': 'El número de teléfono no existe.'})
            else:
                # Procesar la recuperación usando el correo electrónico
                if user.correo == correo:
                    # Aquí puedes enviar el mensaje de recuperación por correo electrónico
                    # Generar código aleatorio
                    codigo = str(random.randint(10000, 99999))
                    
                    # Enviar el código por correo electrónico
                    email = send_mail(
                        'Código de recuperación',
                        f'Su código de recuperación es: {codigo}',
                        'noreply@example.com',
                        [correo],
                        fail_silently=False,
                    )
                    if email:
                        # Guardar el código en el campo 'codigo' del usuario
                        user.codigo = codigo
                        user.save()

                        # Programar la tarea para restablecer el código después de 1 minuto
                        # celery_app.send_task('comedor_django.tasks.reset_codigo', args=[user.id_usuario], eta=datetime.now() + timedelta(minutes=1))
                        timer = threading.Timer(60, reset_codigo, args=[id_usuario])
                        timer.start()
                        
                        return JsonResponse({'mensaje': 'Se ha enviado un mensaje de recuperación.', 'id_usuario': id_usuario})
                    else:
                        return JsonResponse({'error': 'Algo falló, error al enviar el mensaje '})    
                else:
                    return JsonResponse({'error': 'La dirección de correo electrónico no existe.'})

        except Exception as e:
            # return JsonResponse({'error': f'Error al procesar la solicitud: {str(e)}'})
            return JsonResponse({'error': f'Error al procesar la solicitud: El usuario no existe'})
    return JsonResponse({'error': 'Método no permitido.'})

@csrf_exempt
def api_validar_codigo(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:

            id_usuario_str=data.get('id_usuario')
            id_usuario = int(id_usuario_str)
            codigo=data.get('codigo')

            user=Usuario.objects.get(id_usuario=id_usuario)
            if user.codigo==codigo:
                return JsonResponse({'mensaje': 'codigo validado exitosamente.','usuario':user.usuario})
            else:
                return JsonResponse({'error': 'codigo incorrecto.'})
            
        
        except Exception as e:

            return JsonResponse({'error': f'Error al procesar la solicitud: {str(e)}'})
    
    return JsonResponse({'error': 'Método no permitido.'})

@csrf_exempt
def api_cambiar_clave(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        try:
            usuario= data.get('usuario')
            clave = data.get('clave')

            user = Usuario.objects.get(usuario= usuario)

            if user:
                user.clave = clave
                user.save()

                return JsonResponse({'mensaje': 'Contraseña cambiada exitosamente.'})
            else:
                return JsonResponse({'error': 'Error al verificar usuario'})
        except Exception as e:
            return JsonResponse({'error': f'Error al procesar la solicitud: {str(e)}'}) 

    return JsonResponse({'error': 'Método no permitido.'})

