from django.contrib import admin

from .models import World
from .models import Location, Encounter


@admin.register(World)
class WorldAdmin(admin.ModelAdmin):
    pass


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    pass

# EOF
