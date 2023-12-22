# Proyecto Chat Django

## Descripción

Proyecto de chat en tiempo real con Django Channels
implementando:

- 1: configurar documentacion
- 2: configurar web socket: canales
- 3: configurar correos
- 4: configurar la base de datos
- 5: configurar usuarios: roles + override + permission + authentication, no eliminar usuarios se desactivan
- 6: configurar los cors
- 7: aplicacion room: id, name, created_at, deleted_at, user_id, al eliminar un chat se cambia el state de sus comentarios: creacion, eliminacion, consulta,
  solo el usuario creador la puede eliminar o editar
- 8: aplicacion comments: id, content, room, created_at, updated_at, CRUD completo
- 9: implementar stored procedure con parametros

### Configuración del entorno virtual

`python -m venv ./env/env1`

### Activar el entorno virtual

`./env/env1/Scripts/activate`

## Pagina oficial de PIP para buscar documentacion de librerias

- Documentacion [Python Install Packege](https://pypi.org/project/pip/)

## Establecer el Idioma del proyecto
- modificar el archivo settings.py
```
LANGUAGE_CODE = 'es'
```

## Instalar las dependencias

##### Instalar django

`pip install django`
##### Instalar django rest framework ✅

`pip install djangorestframework`

- Documentacion [djangorestframework](https://www.django-rest-framework.org/)
- requiere configurar el archivo settings.py, para agrear rest_framework

##### Instalar drf-yasg ✅

`pip install -U drf-yasg`

- requiere configurar el archivo settings.py, para agrear drf_yasg
- requiere configurar el archivo settings.py, para definir rutas estaticas
- requiere configurar el archivo urls.py, para agrear drf_yasg
- Documentacion [drf-yasg](https://drf-yasg.readthedocs.io/en/stable/readme.html)
  `pip install setuptools`
- Se debe instalar para que funcione correctamente otras dependencias
- generar achivos estaticos
  `python manage.py collectstatic`
- agregar los archivos estaticos a settings.py
```
STATIC_URL = '/static/'
STATIC_ROOT = './static/'
```

##### Instalar django-cors-headers ✅

`pip install django-cors-headers`

- Documentacion [django-cors-headers](https://pypi.org/project/django-cors-headers/)
- requiere configurar el archivo settings.py, para agrear corsheaders
```
INSTALLED_APPS = [
    ...,
    "corsheaders",
    ...,
]

MIDDLEWARE = [
    ...,
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    ...,
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",#local react
]
```

##### Instalar channels

`pip install channels`  ✅

- Documentacion [channels](https://channels.readthedocs.io/en/stable/installation.html)
```

INSTALLED_APPS = [
     ...,
    'channels',
     ...,
]

ASGI_APPLICATION = 'chat_api.asgi.application'


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

CHANNELS_ALLOWED_HOSTS = ['*']


```
- crear la aplicacion que consume los canales
- configurar el archivo consumers.py de la aplicacion
- configurar el canal en el archivo routing.py de la aplicacion

##### Instalar JWT
  `pip install djangorestframework_simplejwt`

* Documentacion [djangorestframework_simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/getting_started.html)

- configurar settings.py
```
import datetime

INSTALLED_APPS = [
    ...
    'rest_framework_simplejwt',
    ...
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )

}

SIMPLE_JWT = { 
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=1), 
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=1), 
}
```

- configurar router.py de la aplicacion users
```
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    ...
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    ...
]

```

- Pagina para configurar el token [jwt.io](https://jwt.io/)

##### Instalar MYSQL

`pip install pymysql`

- Documentacion [pymysql](https://pypi.org/project/pymysql/)
- Configurar settings
  `import pymysql`
  `pymysql.version_info = (1, 4, 6, 'final', 0)`
  `pymysql.install_as_MySQLdb()`

## Permitir texto enriquesido
```pip install django-ckeditor```

`DATABASES = {`
      `default': {`
        `'ENGINE': 'django.db.backends.mysql',`
        `'NAME': 'bd_chat',`
        `'USER': 'root',`
        `'PASSWORD': '',`
        `'HOST': 'localhost',`
        `'PORT': '3306',`
        `'OPTIONS': {`
            `'charset': 'utf8mb4',`
        `},`
   ` }`
`}`

- configuracion de email en settings.py
  `EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' `
  `EMAIL_HOST = 'smtp.gmail.com'`
  `EMAIL_USE_TLS = True`
  `EMAIL_PORT = 587`
  `EMAIL_HOST_USER ='correo'`
  `EMAIL_HOST_PASSWORD = 'contraseña unica'`
  `EMAIL_TIMEOUT = 300`
  `DEFAULT_FROM_EMAIL = EMAIL_HOST_USER`

- crear un archivo llamado email.py en la carpeta utils
- configurar el archivo email.py

## Arquitectura del proyecto

- crear el proyecto
  `django-admin startproject chat_api`
- agregar el proyecto a settings.py

##### crear aplicacion users
  `django-admin startapp users`
* agregar la aplicacion a settings.py
* definir la aplicacion como auth_user_model en settings.py
* configurar el admin.py
* configurar el modelo
* crear la carpeta api
* crear archivo serializers.py
* crear archivo views.py
* crear archivo routers.py
* agregar la aplicacion a urls.py
##### Override User
- modificar el archivo settings.py
```
AUTH_USER_MODEL = 'user.User'
```
- configurar el archivo models.py
- cambiar registro de superusuario
```
USERNAME_FIELD = 'email'
REQUIRED_FIELDS = ['username','first_name', 'last_name']
```


##### crear super usuario
```python manage.py createsuperuser```

##### crear aplicacion room
```django-admin startapp room```

##### crear aplicacion comments
```django-admin startapp comments```


## Produccion 
* generar archivo requirements.txt
```pip freeze > requirements.txt```


