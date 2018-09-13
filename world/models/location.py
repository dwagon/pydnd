from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


##############################################################################
class Location(models.Model):
    world = models.ForeignKey('World', blank=True, on_delete=models.CASCADE, related_name='locations')
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

# EOF
