from django.contrib import admin
from django.urls import path,include
# libreria drf_yasg
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
# router de las apps
from users.api.router import urlpatterns as users_urls
from rooms.api.router import urlpatterns as rooms_urls
from comments.api.router import urlpatterns as commets_urls
from notification.api.router import urlpatterns as notification_urls
# libreria jwt
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# libreria drf_yasg configuracion
name_api = 'Chat'
schema_view = get_schema_view(
   openapi.Info(
      title=f"Documentación de la API {name_api}",
      default_version='v1',
      description=f"Documentación de la API {name_api}",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="practicaprograuniversidad@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    #panel admin
    path('admin/', admin.site.urls),
    #documentacion
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redocs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    #auth - jwt - users
    path('api/', include('users.api.router')), 
    path('api/', include('rooms.api.router')),
    path('api/', include('comments.api.router')),
    path('api/', include('notification.api.router')),
    
]