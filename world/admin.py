from django.contrib import admin

from .models import World
from .models import Location, Encounter
from .models import Wall, Arena


@admin.register(World)
class WorldAdmin(admin.ModelAdmin):
    pass


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    pass


@admin.register(Arena)
class WallArena(admin.ModelAdmin):
    pass


@admin.register(Wall)
class WallAdmin(admin.ModelAdmin):
    pass

# EOF
