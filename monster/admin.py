from django.contrib import admin
from .models import Monster, MonsterState


@admin.register(Monster)
class MonsterAdmin(admin.ModelAdmin):
    pass


@admin.register(MonsterState)
class MonsterStateAdmin(admin.ModelAdmin):
    pass

# EOF
