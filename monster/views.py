from .models import Monster
from .serializers import MonsterSerializer
from rest_framework import generics


##############################################################################
class MonsterList(generics.ListCreateAPIView):
    serializer_class = MonsterSerializer

    def get_queryset(self):
        queryset = Monster.objects.all()

        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name=name)

        return queryset


##############################################################################
class MonsterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Monster.objects.all()
    serializer_class = MonsterSerializer


# EOF
