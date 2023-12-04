# Proyecto Chat Django

## Descripción
Proyecto de chat en tiempo real con Django Channels
implementando: 
* 1: configurar documentacion
* 2: configurar web socket: canales
* 3: configurar correos
* 4: configurar la base de datos
* 5: configurar usuarios: roles + override + permission + authentication, no eliminar usuarios se desactivan
* 6: configurar los cors
* 7: aplicacion room: id, name, created_at, deleted_at, user_id, al eliminar un chat se cambia el state de sus comentarios: creacion, eliminacion, consulta,
solo el usuario creador la puede eliminar o editar
* 8: aplicacion comments: id, content, room, created_at, updated_at, CRUD completo
* 9: implementar stored procedure con parametros

### Configuración del entorno virtual
```python -m venv ./env/env1```

### Activar el entorno virtual
```./env/env1/Scripts/activate```

## Pagina oficial de PIP para buscar documentacion de librerias
* Documentacion [Python Install Packege](https://pypi.org/project/pip/)

### Instalar las dependencias
* Instalar django
```pip install django```
* Instalar django rest framework
```pip install djangorestframework```
- Documentacion [djangorestframework](https://www.django-rest-framework.org/)
- requiere configurar el archivo settings.py, para agrear rest_framework
* Instalar drf-yasg
```pip install -U drf-yasg```
- requiere configurar el archivo settings.py, para agrear drf_yasg
- requiere configurar el archivo settings.py, para definir rutas estaticas
- requiere configurar el archivo urls.py, para agrear drf_yasg
- Documentacion [drf-yasg](https://drf-yasg.readthedocs.io/en/stable/readme.html)
```pip install setuptools```
- Se debe instalar para que funcione correctamente otras dependencias
* Instalar django-cors-headers
```pip install django-cors-headers```
- Documentacion [django-cors-headers](https://pypi.org/project/django-cors-headers/)
* Instalar channels
```pip install channels```
- Documentacion [channels](https://channels.readthedocs.io/en/stable/installation.html)
* Instalar JWT
```pip install djangorestframework_simplejwt```
- Documentacion [djangorestframework_simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/getting_started.html)
* Instalar MYSQL
```pip install pymysql```
- Documentacion [pymysql](https://pypi.org/project/pymysql/)

### Arquitectura del proyecto
* crear el proyecto
```django-admin startproject chat_api```
* agregar el proyecto a settings.py
* crear aplicacion users
```django-admin startapp users```
- agregar la aplicacion a settings.py
- definir la aplicacion como auth_user_model en settings.py
- configurar el admin.py 
- configurar el modelo 
- crear la carpeta api
- crear archivo serializers.py
- crear archivo views.py
- crear archivo routers.py 
- agregar la aplicacion a urls.py
