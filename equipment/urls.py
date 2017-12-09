from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from equipment import views

urlpatterns = [
    url(r'^$', views.EquipmentList.as_view(), name='equipment-list'),
    url(r'^(?P<pk>[0-9]+)/$', views.EquipmentDetail.as_view(), name='equipment-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
