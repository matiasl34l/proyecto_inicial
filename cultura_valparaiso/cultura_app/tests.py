from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Etiqueta, Evento, Guardado, Usuario
from .recomendaciones import recomendar


class CuentasYPreferenciasTests(TestCase):
    def setUp(self):
        self.etiquetas = [
            Etiqueta.objects.get_or_create(nombre='Música')[0],
            Etiqueta.objects.get_or_create(nombre='Teatro')[0],
            Etiqueta.objects.get_or_create(nombre='Arte')[0],
        ]
        self.cuenta = get_user_model().objects.create_user(
            username='persona1',
            password='Una-Clave-Segura-2026!',
        )

    def iniciar_sesion(self, cuenta=None):
        self.client.force_login(cuenta or self.cuenta)

    def datos_perfil(self, gustos=None, distancia='10'):
        return {
            'gustos': gustos or [str(self.etiquetas[0].pk), str(self.etiquetas[1].pk)],
            'latitud': '-33.0472',
            'longitud': '-71.6127',
            'ubicacion_confirmada': 'true',
            'distancia_maxima': distancia,
        }

    def test_home_requires_login(self):
        respuesta = self.client.get(reverse('inicio'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url.split('?')[0], reverse('ingresar'))
        self.assertIn('next=', respuesta.url)

    def test_new_account_must_complete_profile_before_map(self):
        respuesta = self.client.post(reverse('registrar'), {
            'username': 'persona_nueva',
            'password1': 'Otra-Clave-Segura-2026!',
            'password2': 'Otra-Clave-Segura-2026!',
        })
        self.assertRedirects(respuesta, reverse('perfil'))
        self.assertTrue(
            get_user_model().objects.filter(username='persona_nueva').exists()
        )

    def test_registration_accepts_simple_numeric_password_of_eight_characters(self):
        respuesta = self.client.post(reverse('registrar'), {
            'username': 'usuario_numerico',
            'password1': '12345678',
            'password2': '12345678',
        })
        self.assertRedirects(respuesta, reverse('perfil'))
        cuenta = get_user_model().objects.get(username='usuario_numerico')
        self.assertTrue(cuenta.check_password('12345678'))

    def test_registration_rejects_password_shorter_than_eight_characters(self):
        respuesta = self.client.post(reverse('registrar'), {
            'username': 'usuario_corto',
            'password1': '1234567',
            'password2': '1234567',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context['form'].has_error('password1'))
        self.assertFalse(
            get_user_model().objects.filter(username='usuario_corto').exists()
        )

    def test_registration_username_is_limited_to_fifty_characters(self):
        respuesta = self.client.post(reverse('registrar'), {
            'username': 'u' * 51,
            'password1': '12345678',
            'password2': '12345678',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context['form'].has_error('username'))
        self.assertFalse(get_user_model().objects.filter(username='u' * 51).exists())

    def test_registration_accepts_username_of_fifty_characters(self):
        username = 'u' * 50
        respuesta = self.client.post(reverse('registrar'), {
            'username': username,
            'password1': '12345678',
            'password2': '12345678',
        })
        self.assertRedirects(respuesta, reverse('perfil'))
        self.assertTrue(get_user_model().objects.filter(username=username).exists())

    def test_profile_requires_at_least_two_active_tastes(self):
        self.iniciar_sesion()
        respuesta = self.client.post(
            reverse('perfil'),
            self.datos_perfil(gustos=[str(self.etiquetas[0].pk)]),
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Usuario.objects.filter(cuenta=self.cuenta).exists())
        self.assertContains(respuesta, 'Selecciona al menos dos gustos.')

    def test_profile_saves_preferences_for_signed_in_account(self):
        self.iniciar_sesion()
        respuesta = self.client.post(reverse('perfil'), self.datos_perfil())
        self.assertRedirects(respuesta, reverse('inicio'))

        perfil = Usuario.objects.get(cuenta=self.cuenta)
        self.assertEqual(perfil.gustos.count(), 2)
        self.assertEqual(perfil.distancia_maxima, 10)
        self.assertAlmostEqual(perfil.latitud, -33.0472)

    def test_distance_must_be_at_least_one_kilometer(self):
        self.iniciar_sesion()
        respuesta = self.client.post(
            reverse('perfil'),
            self.datos_perfil(distancia='0'),
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context['form'].has_error('distancia_maxima'))
        self.assertContains(respuesta, 'El valor debe ser mayor o igual que 1.')
        self.assertFalse(Usuario.objects.filter(cuenta=self.cuenta).exists())

    def test_distance_validation_messages_are_in_spanish(self):
        self.iniciar_sesion()
        respuesta = self.client.post(
            reverse('perfil'),
            self.datos_perfil(distancia='mucho'),
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Ingresa un número entero válido.')
        self.assertNotContains(respuesta, 'Enter a whole number.')

    def test_profile_requires_confirming_a_location(self):
        self.iniciar_sesion()
        datos = self.datos_perfil()
        datos.pop('ubicacion_confirmada')
        respuesta = self.client.post(reverse('perfil'), datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context['form'].has_error('ubicacion_confirmada'))
        self.assertFalse(Usuario.objects.filter(cuenta=self.cuenta).exists())

    def test_user_without_profile_is_sent_to_own_profile_setup(self):
        otra_cuenta = get_user_model().objects.create_user(
            username='persona2',
            password='Otra-Clave-Segura-2026!',
        )
        self.iniciar_sesion(otra_cuenta)
        respuesta = self.client.get(reverse('inicio'))
        self.assertRedirects(respuesta, reverse('perfil'))

    def test_map_shows_active_events_and_search_ignores_user_preferences(self):
        self.iniciar_sesion()
        self.client.post(reverse('perfil'), self.datos_perfil())
        evento = Evento.objects.create(
            nombre='Festival independiente',
            fecha='2026-12-01',
            direccion='Plaza central',
            descripcion='Actividad para buscar aunque no coincida con los gustos',
            latitud=-33.05,
            longitud=-71.62,
        )
        evento.etiquetas.add(self.etiquetas[2])

        respuesta = self.client.get(reverse('inicio'), {'q': 'Festival'})

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Festival independiente')
        self.assertEqual(
            [resultado.pk for resultado in respuesta.context['resultados_busqueda']],
            [evento.pk],
        )
        self.assertEqual(
            [marcador['id'] for marcador in respuesta.context['eventos_mapa']],
            [evento.pk],
        )


class GuardadosTests(TestCase):
    def setUp(self):
        self.etiqueta = Etiqueta.objects.get_or_create(nombre='Música')[0]
        self.cuenta1 = get_user_model().objects.create_user(username='persona1', password='Clave-Segura-2026!')
        self.cuenta2 = get_user_model().objects.create_user(username='persona2', password='Clave-Segura-2026!')
        self.usuario1 = Usuario.objects.create(cuenta=self.cuenta1, nombre='persona1', distancia_maxima=10)
        self.usuario2 = Usuario.objects.create(cuenta=self.cuenta2, nombre='persona2', distancia_maxima=10)
        self.evento = Evento.objects.create(
            nombre='Concierto en el puerto',
            fecha='2026-12-01',
            direccion='Muelle Prat',
            descripcion='Concierto de prueba',
            latitud=-33.039,
            longitud=-71.625,
        )
        self.evento.etiquetas.add(self.etiqueta)

    def test_guardar_requires_login(self):
        respuesta = self.client.post(reverse('guardar_evento', args=[self.evento.pk]))
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url.split('?')[0], reverse('ingresar'))
        self.assertEqual(Guardado.objects.count(), 0)

    def test_guardar_only_accepts_post(self):
        self.client.force_login(self.cuenta1)
        respuesta = self.client.get(reverse('guardar_evento', args=[self.evento.pk]))
        self.assertEqual(respuesta.status_code, 405)

    def test_guardar_creates_saved_event_for_current_user(self):
        self.client.force_login(self.cuenta1)
        respuesta = self.client.post(reverse('guardar_evento', args=[self.evento.pk]))
        self.assertRedirects(respuesta, reverse('inicio'), fetch_redirect_response=False)
        self.assertTrue(Guardado.objects.filter(usuario=self.usuario1, evento=self.evento).exists())

    def test_guardar_twice_removes_the_event(self):
        self.client.force_login(self.cuenta1)
        self.client.post(reverse('guardar_evento', args=[self.evento.pk]))
        self.client.post(reverse('guardar_evento', args=[self.evento.pk]))
        self.assertEqual(Guardado.objects.count(), 0)

    def test_database_rejects_duplicate_saved_event(self):
        from django.db import IntegrityError, transaction
        Guardado.objects.create(usuario=self.usuario1, evento=self.evento)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Guardado.objects.create(usuario=self.usuario1, evento=self.evento)

    def test_inactive_event_cannot_be_saved(self):
        self.evento.activo = False
        self.evento.save()
        self.client.force_login(self.cuenta1)
        respuesta = self.client.post(reverse('guardar_evento', args=[self.evento.pk]))
        self.assertEqual(respuesta.status_code, 404)

    def test_external_next_url_is_ignored(self):
        self.client.force_login(self.cuenta1)
        respuesta = self.client.post(
            reverse('guardar_evento', args=[self.evento.pk]),
            {'next': 'https://sitio-externo.example/'},
        )
        self.assertRedirects(respuesta, reverse('inicio'), fetch_redirect_response=False)

    def test_saved_list_shows_only_own_events(self):
        otro = Evento.objects.create(
            nombre='Evento de otra persona', fecha='2026-12-02', direccion='Cerro Alegre',
            descripcion='x', latitud=-33.04, longitud=-71.62,
        )
        Guardado.objects.create(usuario=self.usuario1, evento=self.evento)
        Guardado.objects.create(usuario=self.usuario2, evento=otro)
        self.client.force_login(self.cuenta1)
        respuesta = self.client.get(reverse('guardados'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Concierto en el puerto')
        self.assertNotContains(respuesta, 'Evento de otra persona')

    def test_saved_list_requires_login(self):
        respuesta = self.client.get(reverse('guardados'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url.split('?')[0], reverse('ingresar'))

    def test_recommendation_card_has_save_button(self):
        teatro = Etiqueta.objects.get_or_create(nombre='Teatro')[0]
        self.evento.etiquetas.add(teatro)
        self.usuario1.gustos.set([self.etiqueta, teatro])
        self.client.force_login(self.cuenta1)
        respuesta = self.client.get(reverse('inicio'))
        self.assertEqual(len(respuesta.context['recomendaciones']), 1)
        self.assertContains(respuesta, reverse('guardar_evento', args=[self.evento.pk]))

    def test_home_marks_saved_events(self):
        Guardado.objects.create(usuario=self.usuario1, evento=self.evento)
        self.client.force_login(self.cuenta1)
        respuesta = self.client.get(reverse('inicio'), {'q': 'Concierto'})
        self.assertContains(respuesta, 'Quitar de guardados')


class RecomendacionesTests(TestCase):
    """Reproduce los casos de prueba Sansano 1 y Sansano 2 del Entregable III."""

    GUSTOS_1 = [
        'Arte', 'Deportes', 'Naturaleza', 'Fiesta', 'Social', 'Comunidad',
        'Aire Libre', 'Feria', 'Bienestar', 'Creatividad', 'Fotografía',
    ]
    GUSTOS_2 = GUSTOS_1 + [
        'Teatro', 'Gastronomía', 'Entretenimiento', 'Tecnología', 'Ciencia',
        'Aprendizaje', 'Emprendimientos', 'Tradiciones', 'Música', 'Cultura', 'Festival',
    ]

    def etiquetas(self, nombres):
        return [Etiqueta.objects.get_or_create(nombre=nombre)[0] for nombre in nombres]

    def crear_evento(self, nombre, latitud, longitud, etiquetas):
        evento = Evento.objects.create(
            nombre=nombre, fecha='2026-12-01', direccion='x', descripcion='x',
            latitud=latitud, longitud=longitud,
        )
        evento.etiquetas.set(self.etiquetas(etiquetas))
        return evento

    def crear_usuario(self, nombre, gustos, latitud, longitud, distancia):
        usuario = Usuario.objects.create(
            nombre=nombre, latitud=latitud, longitud=longitud, distancia_maxima=distancia,
        )
        usuario.gustos.set(self.etiquetas(gustos))
        return usuario

    def setUp(self):
        self.feria = self.crear_evento(
            'Feria Gastronómica', -33.039, -71.625,
            ['Gastronomía', 'Aire Libre', 'Feria', 'Festival'],
        )
        self.festival = self.crear_evento(
            'Festival de Rock Costero', -33.045, -71.62,
            ['Entretenimiento', 'Música', 'Festival'],
        )
        self.expo = self.crear_evento(
            'Expo Fotografía', -33.041, -71.628, ['Arte', 'Cultura', 'Fotografía'],
        )

    def test_sansano_1(self):
        usuario = self.crear_usuario('Sansano 1', self.GUSTOS_1, -33.0482, -71.6107, 20)
        resultado = recomendar(usuario, list(Evento.objects.all()))
        self.assertEqual(
            [(r['evento'].nombre, r['coincidencias']) for r in resultado],
            [('Feria Gastronómica', 2), ('Expo Fotografía', 2)],
        )

    def test_sansano_2(self):
        usuario = self.crear_usuario('Sansano 2', self.GUSTOS_2, -33.041, -71.615, 30)
        resultado = recomendar(usuario, list(Evento.objects.all()))
        self.assertEqual(
            [(r['evento'].nombre, r['coincidencias']) for r in resultado],
            [('Feria Gastronómica', 4), ('Festival de Rock Costero', 3), ('Expo Fotografía', 3)],
        )
