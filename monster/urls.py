from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from monster import views

urlpatterns = [
    url(r'^$', views.MonsterList.as_view(), name='monster-list'),
    url(r'^(?P<pk>[0-9]+)/$', views.MonsterDetail.as_view(), name='monster-detail'),
    url(r'^state/$', views.MonsterStateList.as_view(), name='monsterstate-list'),
    url(r'^state/(?P<pk>[0-9]+)/$', views.MonsterStateDetail.as_view(), name='monsterstate-detail')
]

urlpatterns = format_suffix_patterns(urlpatterns)

# EOF
