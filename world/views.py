from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Encounter
import os
import json


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
def encounter(request):
    if request.method == "POST":
        e = Encounter(arena_x=20, arena_y=20)
        e.save()
        e.make_map()
        mp = {'map': e.map_repr()}
        return JsonResponse(mp)


##############################################################################
def get_pcs(request):
    pass    # TODO

# EOF
