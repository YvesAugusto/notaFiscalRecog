from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token
from django.urls import re_path as url
from app import views

urlpatterns = [
    url(r'^api/api-token-auth', obtain_auth_token, name='apiTokenAuth'),
    url(r'^api/validate-nota', views.ValidateNota.as_view(), name='validateNota'),
    url(r'^api/esquema/', views.SchemePOST.as_view(), name='schemePOST'),
    url(r'^api/esquemaGPD/\d', views.SchemeGPD.as_view(), name='schemeGPD'),
]
# urlpatterns = format_suffix_patterns(urlpatterns)