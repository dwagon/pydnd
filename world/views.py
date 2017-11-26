from django.http import JsonResponse, HttpResponse
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
def get_pcs(request):
    pass    # TODO

# EOF
