# Generated by Django 4.2.3 on 2023-08-13 00:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("comedor_django", "0005_usuario_correo_usuario_telefono"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuario",
            name="codigo",
            field=models.CharField(default="n/a", max_length=20),
        ),
    ]
