from .models import Character
from .serializers import CharacterSerializer
from equipment.serializers import EquipmentSerializer
from rest_framework import generics
from rest_framework import ModelViewSet


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
class InventoryList(generics.ListCreateAPIView):
    queryset = Character.objects.all()
    serializer_class = EquipmentSerializer


##############################################################################
class InventoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Character.objects.all()
    serializer_class = EquipmentSerializer

# EOF
