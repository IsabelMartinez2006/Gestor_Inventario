from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id_usuario', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('correo', models.EmailField(max_length=150, unique=True)),
                ('contrasena', models.CharField(max_length=255)),
                ('rol', models.CharField(choices=[('administrador', 'Administrador'), ('empleado', 'Empleado')], default='empleado', max_length=15)),
                ('intentos_fallidos', models.PositiveSmallIntegerField(default=0)),
                ('bloqueado_hasta', models.DateTimeField(blank=True, null=True)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'usuarios',
                'ordering': ['nombre'],
            },
        ),
    ]
