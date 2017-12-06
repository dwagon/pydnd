from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^map/(?P<level>\S+)', views.levelmap),
    url(r'^tileset/(?P<tiles>\S+)', views.tileset),
    url(r'^tile/(?P<tilename>\S+)', views.tile),
    url(r'^encounter/', views.g_encounter),
    url(r'get_pcs', views.get_pcs)
]
