from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from encounter import views

urlpatterns = [
    url(r'^$', views.EncounterList.as_view(), name='encounter-list'),
    url(r'^(?P<pk>[0-9]+)/$', views.EncounterDetail.as_view(), name='encounter-detail'),

    url(r'^(?P<pk>[0-9]+)/monster/$', views.MonsterList.as_view(), name='encounter-monster-list'),
    url(r'^(?P<pk>[0-9]+)/monster/(?P<monster>[0-9]+)$', views.MonsterViewSet.as_view({'post': 'assign', 'delete': 'remove'}), name='encounter-monster-detail'),
    url(r'^(?P<pk>[0-9]+)/start_encounter/$', views.start_encounter, name='encounter-start'),

    url(r'^(?P<pk>[0-9]+)/combat_phase/$', views.combat_phase, name='encounter-combat-phase'),
    url(r'^(?P<pk>[0-9]+)/arena/$', views.ArenaViewSet.as_view({'get': 'getmap'}), name='encounter-arena'),
]

urlpatterns = format_suffix_patterns(urlpatterns)

# EOF
