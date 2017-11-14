from django.contrib import admin
from .models import Monster


@admin.register(Monster)
class MonsterAdmin(admin.ModelAdmin):
    pass

# EOF
