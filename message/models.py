from django.db import models


class Message(models.Model):
    world = models.ForeignKey('world.World', on_delete=models.CASCADE)
    msg = models.CharField(max_length=200)


# EOF
