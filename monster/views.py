from .models import Monster, MonsterState
from .serializers import MonsterSerializer, MonsterStateSerializer
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


##############################################################################
class MonsterStateList(generics.ListCreateAPIView):
    serializer_class = MonsterStateSerializer

    def get_queryset(self):
        queryset = MonsterState.objects.all()

        enc = self.request.query_params.get('encounter', None)
        if enc is not None:
            queryset = queryset.filter(encounter=enc)

        return queryset


##############################################################################
class MonsterStateDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MonsterState.objects.all()
    serializer_class = MonsterStateSerializer


# EOF
