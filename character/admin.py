from django.contrib import admin

from .models import Spell, Equipment
from .models import Character


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    pass


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    pass


@admin.register(Spell)
class SpellAdmin(admin.ModelAdmin):
    pass

# EOF
