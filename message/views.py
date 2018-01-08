from .models import Message
from .serializers import MessageSerializer

from rest_framework import generics


##############################################################################
class MessageList(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


##############################################################################
class MessageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


# EOF
