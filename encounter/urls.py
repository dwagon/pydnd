from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from encounter import views

urlpatterns = [
    url(r'^$', views.EncounterList.as_view(), name='encounter-list'),
    url(r'^(?P<pk>[0-9]+)/$', views.EncounterDetail.as_view(), name='encounter-detail')
    # url(r'^(?P<pk>[0-9]+)/monster/$', views.EncounterDetail.as_view(), name='encounter-detail')
    # url(r'^(?P<pk>[0-9]+)/monster/$', views.EncounterDetail.as_view(), name='encounter-detail')
]

urlpatterns = format_suffix_patterns(urlpatterns)

# EOF
