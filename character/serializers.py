from rest_framework import serializers
from .models import EquipState, SpellState, Character, Spell


##############################################################################
class EquipStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipState
        fields = '__all__'


##############################################################################
class SpellStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpellState
        fields = '__all__'


##############################################################################
class SpellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spell
        fields = '__all__'


##############################################################################
class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = '__all__'


##############################################################################
class CharacterShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = '__all__'

# EOF
