from rest_framework import serializers
from .models import Monster, MonsterState, MonsterAttack


##############################################################################
class MonsterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monster
        fields = '__all__'


##############################################################################
class MonsterStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonsterState
        fields = '__all__'


##############################################################################
class MonsterAttackSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonsterAttack
        fields = '__all__'

# EOF
