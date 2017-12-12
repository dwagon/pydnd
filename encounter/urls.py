from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from encounter import views

urlpatterns = [
    url(r'^$', views.EncounterList.as_view(), name='encounter-list'),
    url(r'^(?P<pk>[0-9]+)/$', views.EncounterDetail.as_view(), name='encounter-detail'),
    url(r'^(?P<pk>[0-9]+)/monster/$', views.MonsterList.as_view(), name='encounter-monster-list'),
    url(r'^(?P<pk>[0-9]+)/monster/(?P<monster>[0-9]+)$', views.MonsterViewSet.as_view({'post': 'assign'}), name='encounter-monster-create')
]

urlpatterns = format_suffix_patterns(urlpatterns)

# EOF
