from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .map_bits import Wall
import sys


##############################################################################
class Location(models.Model):
    arena = models.ForeignKey('Arena', blank=True, on_delete=models.CASCADE)
    x = models.IntegerField(default=-1)
    y = models.IntegerField(default=-1)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        try:
            return "{} at {}, {}".format(self.content_object.name, self.x, self.y)
        except AttributeError:
            return "Unknown at {}, {}".format(self.x, self.y)


##############################################################################
class Arena(models.Model):
    world = models.ForeignKey('world.World', on_delete=models.CASCADE)
    arena_x = models.IntegerField(default=0)
    arena_y = models.IntegerField(default=0)

    ##########################################################################
    def make_map(self):
        for x in range(self.arena_x):
            self.set_location(Wall(), x, 0)
            self.set_location(Wall(), x, self.arena_y-1)
        for y in range(self.arena_y):
            self.set_location(Wall(), 0, y)
            self.set_location(Wall(), self.arena_x, y)
        self.save()

    ##########################################################################
    def __getitem__(self, loc):
        try:
            l = Location.objects.get(arena=self, x=loc[0], y=loc[1])
            return l.content_object
        except ObjectDoesNotExist:
            return None

    ##########################################################################
    def delete(self, x, y):
        l = Location.objects.filter(arena=self, x=x, y=y)
        l.delete()

    ##########################################################################
    def change_loc(self, oldx, oldy, newx, newy):
        l = Location.objects.get(arena=self, x=oldx, y=oldy)
        l.x, l.y = newx, newy
        l.save()
        return l

    ##########################################################################
    def clear(self):
        for l in Location.objects.all():
            l.delete()

    ##########################################################################
    def move(self, obj, drn):
        dirmap = {
                'N': (-1, 0),
                'S': (1, 0),
                'E': (0, 1),
                'W': (0, -1)
                }
        targx = obj.x + dirmap[drn][0]
        targy = obj.y + dirmap[drn][1]
        if self[(targx, targy)]:
            print("{} Movement blocked by {}".format(obj.name, self[(targx, targy)].name))
            return False

        print("{} moved from {},{} {} to {}, {}".format(obj.name, obj.x, obj.y, drn, targx, targy))
        self.change_loc(obj.x, obj.y, targx, targy)
        obj.x, obj.y = targx, targy
        obj.save()
        return True

    ##########################################################################
    def all_animate(self):
        return [o.content_object for o in Location.objects.filter(arena=self) if o.content_object.animate]

    ##########################################################################
    def __str__(self):
        m = []
        for x in range(0, self.arena_x):
            ycol = []
            for y in range(0, self.arena_y):
                l = Location.objects.filter(arena=self, x=x, y=y)
                if not l:
                    ycol.append('.')
                    continue
                elif isinstance(l[0].content_object, Wall):
                    ycol.append('X')
                else:
                    sys.stderr.write("{}, {} = {}".format(x, y, type(l[0].content_object)))
                    ycol.append('?')
            m.append("".join(ycol))
        return "\n".join(m)

    ##########################################################################
    def print_arena(self, out=sys.stdout):
        arena = {}
        for i in Location.objects.filter(arena=self):
            arena[(i.x, i.y)] = i.content_object
        for x in range(self.arena_x):
            for y in range(self.arena_y):
                if (x, y) in arena:
                    out.write("{:4} ".format(arena[(x, y)].name[:5]))
                else:
                    out.write("{:4} ".format("_"))
            out.write("\n")
        out.write("\n")

    ##########################################################################
    def set_location(self, obj, x, y):
        obj.x = x
        obj.y = y
        obj.save()
        l = Location(arena=self, x=x, y=y, content_object=obj)
        l.save()

# EOF
