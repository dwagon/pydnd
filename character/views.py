from .models import Character
from .serializers import CharacterSerializer
from .serializers import EquipStateSerializer

from django.shortcuts import get_object_or_404

from equipment.serializers import EquipmentSerializer
from equipment.models import Equipment

from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


##############################################################################
class CharacterViewSet(ModelViewSet):
    serializer_class = CharacterSerializer
    queryset = Character.objects.all()


##############################################################################
class CharacterList(generics.ListCreateAPIView):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer


##############################################################################
class CharacterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer


##############################################################################
class InventoryViewSet(viewsets.ModelViewSet):
    serializer_class = EquipmentSerializer

    def get_queryset(self):
        char = Character.objects.get(pk=self.kwargs['pk'])
        queryset = char.gear.all()
        return queryset

#    def list(self, request):
#        pass
#
    def equip(self, request, **kwargs):
        char = Character.objects.get(pk=self.kwargs['pk'])
        equip = Equipment.objects.get(pk=self.kwargs['inv_pk'])
        ready = request.data.get('ready', False)
        gear = char.equip(equip, ready)

        serializer = EquipStateSerializer(gear)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        pass

#    def update(self, request, pk=None):
#        pass
#
#    def partial_update(self, request, pk=None):
#        pass
#
#    def destroy(self, request, pk=None):
#        pass


# EOF
