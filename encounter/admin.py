from django.contrib import admin
from .models import Encounter


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    pass

# EOF
