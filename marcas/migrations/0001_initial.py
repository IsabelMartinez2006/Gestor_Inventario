from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Marca',
            fields=[
                ('id_marca', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'db_table': 'marcas',
                'ordering': ['nombre'],
            },
        ),
    ]
