from rest_framework import serializers
from .models import Equipment, EquipState, SpellState, Character, Spell


##############################################################################
class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ('name', 'category', 'cost', 'weight', 'magic', 'damage', 'reach', 'ac_base', 'ac_modifier')


##############################################################################
class EquipStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipState
        fields = ('world', 'name', 'charclass', 'race', 'gender', 'align', 'x', 'y', 'stat_str', 'bonus_str', 'stat_int', 'stat_wis', 'stat_dex', 'stat_con', 'stat_cha')


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

# EOF
