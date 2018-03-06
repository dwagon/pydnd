from rest_framework import serializers
from .models import Equipment


##############################################################################
class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ('id', 'name', 'category', 'cost', 'weight')


# EOF
