from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from character import views


urlpatterns = [
    url(r'^$', views.CharacterList.as_view(), name='character-list'),
    url(r'^(?P<pk>[0-9]+)/$', views.CharacterDetail.as_view(), name='character-detail'),
    url(r'^(?P<pk>[0-9]+)/equip/$', views.InventoryViewSet.as_view({'get': 'list'}), name='inventory-list'),
    url(r'^(?P<pk>[0-9]+)/equip/(?P<inv_pk>[0-9]+)$', views.InventoryViewSet.as_view({'get': 'retrieve', 'post': 'create'}), name='inventory-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
