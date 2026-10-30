from django.db import migrations, models


ETIQUETAS_INICIALES = [
    'Música',
    'Teatro',
    'Arte',
    'Cultura',
    'Gastronomía',
    'Deportes',
    'Naturaleza',
    'Entretenimiento',
    'Fiesta',
    'Social',
    'Comunidad',
    'Aire Libre',
    'Tecnología',
    'Ciencia',
    'Aprendizaje',
    'Ferias',
    'Emprendimientos',
    'Bienestar',
    'Creatividad',
    'Tradiciones',
]


def crear_etiquetas_y_migrar_existentes(apps, schema_editor):
    Etiqueta = apps.get_model('cultura_app', 'Etiqueta')
    Evento = apps.get_model('cultura_app', 'Evento')
    alias = schema_editor.connection.alias

    for nombre in ETIQUETAS_INICIALES:
        Etiqueta.objects.using(alias).get_or_create(nombre=nombre)

    for evento in Evento.objects.using(alias).all().iterator():
        nombres = (evento.etiquetas_texto_antiguo or '').split(',')
        for nombre in nombres:
            nombre = nombre.strip()
            if nombre:
                etiqueta, _ = Etiqueta.objects.using(alias).get_or_create(nombre=nombre)
                evento.etiquetas.add(etiqueta)


class Migration(migrations.Migration):

    dependencies = [
        ('cultura_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Etiqueta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.RenameField(
            model_name='evento',
            old_name='etiquetas',
            new_name='etiquetas_texto_antiguo',
        ),
        migrations.AddField(
            model_name='evento',
            name='hora',
            field=models.TimeField(null=True),
        ),
        migrations.AddField(
            model_name='evento',
            name='etiquetas',
            field=models.ManyToManyField(blank=True, related_name='eventos', to='cultura_app.etiqueta'),
        ),
        migrations.RunPython(crear_etiquetas_y_migrar_existentes, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='evento',
            name='etiquetas_texto_antiguo',
        ),
    ]
