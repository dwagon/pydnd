from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from character import views

urlpatterns = [
    url(r'^$', views.CharacterList.as_view(), name='character-list'),
    url(r'^(?P<pk>[0-9]+)/$', views.CharacterDetail.as_view(), name='character-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
