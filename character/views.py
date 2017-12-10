from .models import Character, EquipState
from .serializers import CharacterSerializer
from equipment.serializers import EquipmentSerializer
from equipment.models import Equipment
from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from rest_framework import mixins
from rest_framework import viewsets


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
        if 'inv_pk' in self.kwargs:
            queryset = queryset.filter(id=self.kwargs['inv_pk'])
        return queryset

#    def list(self, request):
#        pass
#
    def create(self, request, **kwargs):
        print("kwargs={}".format(self.kwargs))
        pass

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
