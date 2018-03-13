from .models import Encounter
from .serializers import EncounterSerializer, LocationSerializer
from monster.models import MonsterState, Monster
from monster.serializers import MonsterStateSerializer
from rest_framework import generics
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


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
        arena = {}
        for i in enc.locations.all():
            loc = "{} {}".format(i.x, i.y)
            arena[loc] = LocationSerializer(i).data
        return Response(arena, status=status.HTTP_200_OK)


##############################################################################
class MonsterViewSet(viewsets.ModelViewSet):
    def assign(self, request, **kwargs):
        """ Assign new monster type to an encounter"""

        enc = Encounter.objects.get(pk=self.kwargs['pk'])
        mon = Monster.objects.get(pk=kwargs['monster'])
        number = request.data.get('number', 1)
        for _ in range(number):
            ms = MonsterState(encounter=enc, monster=mon)
            ms.name = "{}{}".format(mon.name, _)
            ms.save()

        monsters = enc.monsters.all()
        serializer = MonsterStateSerializer(monsters, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove(self, request, **kwargs):
        """ Remove the monster state """
        enc = Encounter.objects.get(pk=self.kwargs['pk'])
        m = enc.monsters.get(pk=self.kwargs['monster'])
        m.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


##############################################################################
@api_view(['POST'])
def start_encounter(request, **kwargs):
    """ Start the encounter"""
    enc = Encounter.objects.get(pk=kwargs['pk'])
    enc.start()
    return Response({}, status=status.HTTP_200_OK)


##############################################################################
@api_view(['POST'])
def place_monster(request, **kwargs):
    """ Place the monsters around the arena """
    enc = Encounter.objects.get(pk=kwargs['pk'])
    enc.place_monsters()
    monsters = enc.monsters.all()
    serializer = MonsterStateSerializer(monsters, many=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


##############################################################################
@api_view(['POST'])
def place_pcs(request, **kwargs):
    enc = Encounter.objects.get(pk=kwargs['pk'])
    enc.place_pcs()
    return Response({"status": "ok"}, status=status.HTTP_201_CREATED)


##############################################################################
@api_view(['POST'])
def combat_phase(request, **kwargs):
    enc = Encounter.objects.get(pk=kwargs['pk'])
    keep_going = enc.combat_phase()

    return Response({"finished": not keep_going}, status=status.HTTP_200_OK)

# EOF
