from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    url(r'^map/(?P<level>\S+)', views.levelmap),
    url(r'^tileset/(?P<tiles>\S+)', views.tileset),
    url(r'^tile/(?P<tilename>\S+)', views.tile),
    url(r'^encounter/', views.g_encounter),
    url(r'get_pcs', views.get_pcs),
    url(r'^$', views.WorldList.as_view(), name='world-list'),
    url(r'^(?P<pk>[0-9]+)/$', views.WorldDetail.as_view(), name='world-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
