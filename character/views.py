from .models import Character
from .serializers import CharacterSerializer
from .serializers import EquipStateSerializer

from equipment.serializers import EquipmentSerializer
from equipment.models import Equipment

from rest_framework import generics
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

import sys


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


@api_view(['POST'])
##############################################################################
def action(request, **kwargs):
    char = Character.objects.get(pk=kwargs['pk'])
    data = {}
    if kwargs['action'] == 'move':
        drn = request.data.get('direction')
        data['ans'] = char.move(direct=drn)
    return Response(data, status=status.HTTP_200_OK)


# EOF
