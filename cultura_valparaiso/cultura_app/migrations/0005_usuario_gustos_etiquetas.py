from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cultura_app', '0004_restaurar_etiqueta_musica'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('distancia_maxima', models.IntegerField()),
                ('gustos', models.ManyToManyField(blank=True, related_name='usuarios', to='cultura_app.etiqueta')),
            ],
        ),
    ]
