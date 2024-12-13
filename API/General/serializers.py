from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from API.General.models import Asset, OldValue, OneYearValue, Currency
from rest_framework.validators import UniqueTogetherValidator


class OldValueSerializer(serializers.ModelSerializer):
    date = serializers.DateField()
    class Meta:
        model = OldValue
        fields = ['date','value']
        extra_kwargs = {
            "date": {'read_only': True},
            "value": {'read_only': True},
        }


class OneYearValueSerializer(serializers.ModelSerializer):
    date = serializers.DateField()
    class Meta:
        model = OneYearValue
        fields = ['date','value']
        extra_kwargs = {
            "date": {'read_only': True},
            "value": {'read_only': True},
        }

class AssetDetailSerializer(ModelSerializer):
    oldValues = serializers.SerializerMethodField()
    oneYearValues = serializers.SerializerMethodField()
    date_value = serializers.DateField()
    class Meta: 
        model = Asset
        fields = '__all__'

    def get_oldValues(self, instance):
        oldValues = OldValue.objects.filter(asset = instance)
        return OldValueSerializer(oldValues, many=True).data
    
    def get_oneYearValues(self, instance):
        oneYearValues = OneYearValue.objects.filter(asset = instance)
        return OneYearValueSerializer(oneYearValues, many=True).data



class AssetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['ticker', 'company', 'type', 'country']

class AssetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['ticker']
        validators = [
            UniqueTogetherValidator(
                queryset=Asset.objects.all(),
                fields=['ticker'],
                message="Cet actif existe déjà"
            )
        ]
