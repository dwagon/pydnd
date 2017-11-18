from django.contrib import admin

from .models import Spell, Equipment
from .models import Character
from .models import SpellState, EquipState


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    pass


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    pass


@admin.register(Spell)
class SpellAdmin(admin.ModelAdmin):
    pass


@admin.register(SpellState)
class SpellStateAdmin(admin.ModelAdmin):
    pass


@admin.register(EquipState)
class EquipStateAdmin(admin.ModelAdmin):
    pass

# EOF
