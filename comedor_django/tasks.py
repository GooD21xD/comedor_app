# En tasks.py
# from celery import shared_task
# from datetime import datetime, timedelta
from .models import Usuario

# @shared_task
def reset_codigo(usuario_id):
    try:
        user = Usuario.objects.get(id_usuario=usuario_id)
        if user.codigo != 'n/a':
            user.codigo = 'n/a'
            user.save()
    except Usuario.DoesNotExist:
        pass

