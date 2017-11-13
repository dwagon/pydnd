from django.contrib import admin

from .models import Spell, Equipment
from .models import Fighter, Cleric, Mage, Thief


@admin.register(Fighter)
class FighterAdmin(admin.ModelAdmin):
    pass


@admin.register(Cleric)
class ClericAdmin(admin.ModelAdmin):
    pass


@admin.register(Mage)
class MageAdmin(admin.ModelAdmin):
    pass


@admin.register(Thief)
class ThiefAdmin(admin.ModelAdmin):
    pass


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    pass


@admin.register(Spell)
class SpellAdmin(admin.ModelAdmin):
    pass

# EOF
