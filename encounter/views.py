from .models import Encounter
from .serializers import EncounterSerializer
from monster.models import MonsterState, Monster
from monster.serializers import MonsterStateSerializer
from rest_framework import generics
from rest_framework import viewsets
from rest_framework import status
from utils import roll
from rest_framework.response import Response


##############################################################################
class EncounterList(generics.ListCreateAPIView):
    queryset = Encounter.objects.all()
    serializer_class = EncounterSerializer


##############################################################################
class EncounterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Encounter.objects.all()
    serializer_class = EncounterSerializer


##############################################################################
class MonsterList(generics.ListCreateAPIView):
    serializer_class = MonsterStateSerializer

    def get_queryset(self):
        queryset = MonsterState.objects.all()
        queryset = queryset.filter(encounter=self.kwargs['pk'])
        return queryset


##############################################################################
class ArenaViewSet(viewsets.ModelViewSet):
    def getmap(self, request, **kwargs):
        enc = Encounter.objects.get(pk=self.kwargs['pk'])
        data = {'map': enc.print_arena()}
        return Response(data)


##############################################################################
class MonsterViewSet(viewsets.ModelViewSet):
    def assign(self, request, **kwargs):
        """ Assign new monster type to an encounter"""

        enc = Encounter.objects.get(pk=self.kwargs['pk'])
        mon = Monster.objects.get(pk=kwargs['monster'])
        number = request.data.get('number', None)
        if number is None:
            number = roll(mon.numappearing)
        for _ in range(number):
            ms = MonsterState(encounter=enc, monster=mon)
            ms.name = "{}{}".format(mon.name, _)
            ms.save()

        monsters = enc.monsters.all()
        serializer = MonsterStateSerializer(monsters, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def place(self, request, **kwargs):
        """ Place the monsters around the arena """
        enc = Encounter.objects.get(pk=self.kwargs['pk'])
        enc.place_monsters()
        monsters = enc.monsters.all()
        serializer = MonsterStateSerializer(monsters, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# EOF
