from rest_framework import serializers
from .models import Encounter, Location
from monster.models import MonsterState
from monster.serializers import MonsterStateSerializer
from character.models import Character
from character.serializers import CharacterShortSerializer

import sys


##############################################################################
class EncounterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Encounter
        fields = '__all__'


##############################################################################
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('x', 'y', 'content')
        read_only_fields = '__all__'

    def to_representation(self, obj):
        data = {
            'x': obj.x,
            'y': obj.y
            }
        if isinstance(obj.content_object, MonsterState):
            data['content'] = MonsterStateSerializer(obj.content_object).data
        elif isinstance(obj.content_object, Character):
            data['content'] = CharacterShortSerializer(obj.content_object).data
        else:
            sys.stderr.write("LocationSerializer: Unhanded {}".format(obj.content_type))
            sys.exit(1)
        return data

# EOF
