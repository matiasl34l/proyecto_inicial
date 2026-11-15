from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Etiqueta, Evento, Usuario


class CuentasYPreferenciasTests(TestCase):
    def setUp(self):
        self.etiquetas = [
            Etiqueta.objects.create(nombre='Música'),
            Etiqueta.objects.create(nombre='Teatro'),
            Etiqueta.objects.create(nombre='Arte'),
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
