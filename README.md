CultiValpo - Grupo 3 
Aplicación web desarrollada en Django para recomendar eventos culturales en Valparaíso según los gustos y la ubicación de cada estudiante (Mapbox GL JS, Nominatim y fórmula de Haversine).

1. Clonar repositorio:
git clone https://github.com/matiasl34l/proyecto_inicial.git

Entrar al directorio:
cd proyecto_inicial

2. Instalar Django:
pip install django

Verificar instalación:
pip show django

3. Configurar token público de Mapbox:
Antes de iniciar el servidor, definir la variable de entorno MAPBOX_ACCESS_TOKEN:

En Windows (PowerShell):
powershell
$env:MAPBOX_ACCESS_TOKEN="tu_token_publico_de_mapbox"

En Linux o macOS:
export MAPBOX_ACCESS_TOKEN="tu_token_publico_de_mapbox"

4. Aplicar migraciones:
Entrar al directorio donde se encuentra manage.py:
cd cultura_valparaiso

Ejecutar (crea la base de datos SQLite y precarga las etiquetas culturales iniciales):
python manage.py migrate

5. Iniciar servidor:
Ejecutar:
python manage.py runserver

Abrir http://127.0.0.1:8000/ en cualquier navegador web.

Uso y datos de prueba:
Para probar la aplicación como estudiante, entrar a http://127.0.0.1:8000/ y seleccionar "Crear cuenta" para registrar un usuario, elegir al menos 2 gustos, seleccionar una ubicación en el mapa y definir la distancia máxima en kilómetros.

Para cargar eventos o revisar etiquetas, usuarios y eventos guardados, acceder al panel de administración:
http://127.0.0.1:8000/admin

Crear superusuario (si no existe):

python manage.py createsuperuser

Completar:
Username
Email
Password

Pruebas automatizadas:
Para ejecutar las 26 pruebas unitarias y de integración (incluidos los casos de prueba Sansano 1 y Sansano 2):
python manage.py test
