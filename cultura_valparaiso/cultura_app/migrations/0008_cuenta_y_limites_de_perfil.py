import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def corregir_distancias_invalidas(apps, schema_editor):
    Usuario = apps.get_model('cultura_app', 'Usuario')
    Usuario.objects.using(schema_editor.connection.alias).filter(
        distancia_maxima__lt=1
    ).update(distancia_maxima=1)


class Migration(migrations.Migration):

    dependencies = [
        ('cultura_app', '0007_activo_en_usuario_etiqueta_evento'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='cuenta',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='perfil_cultural',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='nombre',
            field=models.CharField(max_length=150),
        ),
        migrations.RunPython(corregir_distancias_invalidas, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='usuario',
            name='distancia_maxima',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddConstraint(
            model_name='usuario',
            constraint=models.CheckConstraint(
                condition=models.Q(('distancia_maxima__gte', 1)),
                name='usuario_distancia_min_1_km',
            ),
        ),
    ]
