from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from encounter.models import Encounter
import os
import json

from .models import World
from .serializers import WorldSerializer
from rest_framework import generics


##############################################################################
class WorldList(generics.ListCreateAPIView):
    queryset = World.objects.all()
    serializer_class = WorldSerializer


##############################################################################
class WorldDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = World.objects.all()
    serializer_class = WorldSerializer


##############################################################################
def levelmap(request, level):
    mapdir = os.path.join('static', 'maps', level)
    f = open(os.path.join(mapdir, 'map.txt'))
    m = f.read().split('\n')
    f.close()

    g = open(os.path.join(mapdir, 'tileset.json'))
    lmap = json.load(g)
    lmap["map"] = m
    return JsonResponse(lmap)


##############################################################################
def tileset(request, tiles):
    f = open(os.path.join('static', 'tileset', "{}.json".format(tiles)))
    d = json.load(f)
    return JsonResponse(d)


##############################################################################
def tile(request, tilename):
    imgfile = os.path.join('static', 'tiles', "{}.png".format(tilename))
    with open(imgfile, "rb") as f:
        return HttpResponse(f.read(), content_type="image/png")


##############################################################################
@csrf_exempt
def g_encounter(request):
    if request.method == "POST":
        e = Encounter(size_x=20, size_y=20)
        e.save()
        e.make_map()
        mp = {'map': e.map_repr()}
        return JsonResponse(mp)


##############################################################################
def get_pcs(request):
    pass    # TODO

# EOF
