from rest_framework import serializers
from .models import Monster, MonsterState


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

# EOF
