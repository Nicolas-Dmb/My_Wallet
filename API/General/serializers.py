from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Asset, OldValue, OneYearValue, Currency
from rest_framework.validators import UniqueTogetherValidator


class OldValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = OldValue
        fields = '__all__'

class OneYearValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = OneYearValue
        fields = '__all__'

class AssetDetailSerializer(ModelSerializer):
    oldValues = serializers.SerializerMethodField()
    oneYearValues = serializers.SerializerMethodField()
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
        validators = [
            UniqueTogetherValidator(
                queryset=Asset.objects.all(),
                fields=['ticker'],
                message="Cet actif existe déjà"
            )
        ]

    def create(self, validated_data):
        ticker = validated_data['ticker']
        
        # Création de l'asset
        response = Asset.create_asset(ticker)
        if response == True:
            try:
                # Création des valeurs associées
                response_OneYear = OneYearValue.create_OneYearValue(ticker)
                response_OldValue = OldValue.create_OldValue(ticker)
                
                # Si l'une des créations échoue, supprimer l'asset et lever une erreur
                if response_OneYear == False or response_OldValue == False:
                    Asset.objects.get(ticker=ticker).delete()
                    raise serializers.ValidationError("Failed to create associated values")
                
                return Asset.objects.get(ticker=ticker)
            
            except Exception as e:
                # Suppression de l'asset en cas d'exception et renvoi d'une erreur
                Asset.objects.get(ticker=ticker).delete()
                raise serializers.ValidationError(f"Error during asset creation: {str(e)}")
        
        elif response == 'Asset already exist':
            asset = Asset.objects.get(ticker=ticker)
            asset.maj_asset(ticker)
            return Asset.objects.get(ticker=ticker)
        else:
            raise serializers.ValidationError(response)





'''
Listasset

create : 
create_asset
create_OneYearValue
create_oldValue'''