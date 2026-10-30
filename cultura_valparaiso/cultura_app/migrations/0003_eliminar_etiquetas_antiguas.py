from django.db import migrations


ETIQUETAS_A_ELIMINAR = {'rock', 'musica', 'festival', 'cultura'}


def eliminar_etiquetas_antiguas(apps, schema_editor):
    Etiqueta = apps.get_model('cultura_app', 'Etiqueta')
    etiquetas = Etiqueta.objects.using(schema_editor.connection.alias)

    for etiqueta in etiquetas.all().iterator():
        if etiqueta.nombre.casefold() in ETIQUETAS_A_ELIMINAR:
            etiqueta.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cultura_app', '0002_evento_hora_etiquetas_multiples'),
    ]

    operations = [
        migrations.RunPython(eliminar_etiquetas_antiguas, migrations.RunPython.noop),
    ]
