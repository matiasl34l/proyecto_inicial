from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cultura_app', '0006_usuario_latitud_usuario_longitud'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='activo',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='etiqueta',
            name='activo',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='evento',
            name='activo',
            field=models.BooleanField(default=True),
        ),
    ]
