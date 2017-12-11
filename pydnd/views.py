from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def api_root(request, format=None):
    return Response({
        'monster': reverse('monster-list', request=request, format=format),
        # 'monsterstate': reverse('monsterstate-list', request=request, format=format),
        'character': reverse('character-list', request=request, format=format),
        'encounter': reverse('encounter-list', request=request, format=format),
        'equipment': reverse('equipment-list', request=request, format=format),
        'world': reverse('world-list', request=request, format=format)
    })

# EOF
