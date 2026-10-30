1. Clonar repositorio:
bash
git clone URL_DEL_REPOSITORIO

Entrar al directorio:
bash
cd proyecto_inicial

2. Instalar Django:
bash
pip install django

Verificar instalación:
bash
pip show django

3. Aplicar migraciones
Entrar al directorio donde se encuentra manage.py:
bash
cd cultura_valparaiso

Ejecutar:
bash
python manage.py makemigrations

Luego:
bash
python manage.py migrate

4. Iniciar servidor
Ejecutar:
bash
python manage.py runserver

Abrir http://127.0.0.1:8000/ desde visual studio code, desde un navegador no se verá.

Datos de prueba:
Para probar la funcionalidad principal se deben crear usuarios y eventos desde el panel de administración.
Acceder a:
http://127.0.0.1:8000/admin

Crear superusuario
Si no existe:
bash
python manage.py createsuperuser

Completar:
Username
Email
Password

Usuarios de prueba:
En el panel de admin en el apartado de "Usuario" seleccionar "+Add" e ingresar:
Usuario 1
Nombre: Sansano 1
Gustos: Arte, Deportes, Naturaleza, Fiesta, Social, Comunidad, Aire Libre, Feria, Bienestar, Creatividad, Fotografia
Distancia máxima: 20
Luego seleccionar "Save and add another"
Usuario 2
Nombre: Sansano 2
Gustos: Seleccionar "Choose all gustos"
Distancia máxima: 30
Luego en "Home" en el apartado de "Usuario" seleccionar "Change" y desmarcar en "ACTIVO" a sansano 2, luego de probar a sansano 1 desmarcar a sansano 1 y marcar a sansao 2, luego de cada vez que se marque o desmarque seleccionar "Save"

Eventos de prueba:
En el panel de admin en el apartado de "Eventos" seleccionar "+Add" e ingresar:
Nombre: Festival Rock Costero
Fecha: Cualquiera
Hora: Cualquiera
Dirección: Av. Brasil
Descripcion: Cualquiera
Latitud: -33.045
Longitud: -71.62
Etiquetas: Entretenimiento, Música, Festival
Save and add another

Nombre: Expo Fotografía
Fecha: Cualquiera
Hora: Cualquiera
Dirección: Cerro Alegre
Descripcion: Cualquiera
Latitud: -33.041
Longitud: -71.628
Etiquetas: Arte, Cultura, Fotografía
Save and add another

Nombre: Feria Gastronomica
Fecha: Cualquiera
Hora: Cualquiera
Dirección: Muelle Prat
Descripcion: Cualquiera
Latitud: -33.039
Longitud: -71.625
Etiquetas: Gastronomía, Aire Libre, Feria, Festival
Save
Luego seleccionar "View Site" para ver en el mapa el caso de sansano 1, luego volver al panel de admin http://127.0.0.1:8000/admin para ver el caso de sansano 2 explicado anteriormente
