"""pydnd URL Configuration
"""
from django.conf.urls import url, include
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.api_root),
    url(r'^admin/', admin.site.urls),
    url(r'^world/', include('world.urls')),
    url(r'^encounter/', include('encounter.urls')),
    url(r'^equipment/', include('equipment.urls')),
    url(r'^character/', include('character.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

# EOF
