from .models import Equipment
from .serializers import EquipmentSerializer
from rest_framework import generics


##############################################################################
class EquipmentList(generics.ListCreateAPIView):
    serializer_class = EquipmentSerializer

    def get_queryset(self):
        queryset = Equipment.objects.all()

        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name=name)

        return queryset


##############################################################################
class EquipmentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer

# EOF
