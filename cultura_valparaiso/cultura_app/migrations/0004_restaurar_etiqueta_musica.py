from django.db import migrations


def restaurar_etiqueta_musica(apps, schema_editor):
    Etiqueta = apps.get_model('cultura_app', 'Etiqueta')
    Etiqueta.objects.using(schema_editor.connection.alias).get_or_create(nombre='Música')


class Migration(migrations.Migration):

    dependencies = [
        ('cultura_app', '0003_eliminar_etiquetas_antiguas'),
    ]

    operations = [
        migrations.RunPython(restaurar_etiqueta_musica, migrations.RunPython.noop),
    ]
