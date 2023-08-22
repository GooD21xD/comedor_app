from django.db import models

class Turno(models.Model):
    id_turno = models.AutoField(primary_key=True)
    turno = models.CharField(max_length=20)
    hora_ini = models.TimeField()
    hora_fin = models.TimeField()
    cant_turno = models.IntegerField(default=0)  # Agregamos un valor predeterminado
    cant_turno_total = models.IntegerField(default=0)  # Agregamos un valor predeterminado
    estado= models.IntegerField(default=0)

    class Meta:
        db_table = 'turnos'  # Especificamos el nombre de la tabla en la base de datos

    def __str__(self):
        return self.turno



class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    usuario = models.CharField(max_length=100)
    clave = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    ape_p = models.CharField(max_length=100)
    ape_m = models.CharField(max_length=100)
    fec_nac = models.DateField()
    correo = models.EmailField(max_length=100, default='n/a')  # Agregar campo de correo electrónico
    telefono = models.CharField(max_length=20, default='n/a')  # Valor predeterminado para el teléfono
    codigo = models.CharField(max_length=20, default='n/a') #codigo para recuperar clave

    class Meta:
        db_table = 'usuario'

    def __str__(self):
        return self.usuario
    

class Reserva(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_reserva')
    id_turno = models.ForeignKey(Turno, on_delete=models.CASCADE, db_column='id_turno')
    id_usuario = models.IntegerField()
    nombre = models.CharField(max_length=100)
    ape_p = models.CharField(max_length=100)
    hora_ini = models.TimeField()
    hora_fin = models.TimeField()
    accion = models.IntegerField()

    class Meta:
            db_table = 'reserva'  # Especificamos el nombre de la tabla en la base de datos
    
    # def __str__(self):
    #     return f'Reserva {self.id_reserva} - {self.nombre} {self.ape_p}'