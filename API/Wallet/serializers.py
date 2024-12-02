from datetime import datetime
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Buy, Sells, Wallet, Asset, Cash, CashDetail, CryptoDetail, BourseDetail, RealEstateDetail, RealEstate, Categories, HistoricalPrice, Crypto, Bourse, Cash, HistoricalWallet, HistoricalBourse, HistoricalCrypto, HistoricalCash,  HistoricalImmo
from rest_framework.validators import UniqueTogetherValidator

class BuySerializer(ModelSerializer):
    class Meta:
        model=Buy
        fields=["currency","name","plateforme","account","number_buy","price_buy","date_buy","ticker"]
        extra_kwargs = {
            'plateforme': {'required': False},
            'account': {'required': False},
        }

class CryptoDetailSerializer(ModelSerializer):
    class Meta:
        model = CryptoDetail
        fields = ["sous_category","stacking","number_stacking"]
        extra_kwargs = {
            'stacking': {'required': False},
            'number_stacking': {'required': False},
        }

class BourseDetailSerializer(ModelSerializer):
    class Meta:
        model = BourseDetail
        fields = ["sous_category","industry"]
        extra_kwargs = {
            'industry': {'required': False},
        }

class CashDetailSerializer(ModelSerializer):
    class Meta:
        model = CashDetail
        fields = ["bank","account", "amount"]

class SellSerializer(ModelSerializer):
    class Meta:
        model = Sells
        fields = ["name","ticker","currency","number_sold","price_sold","date_sold","plateforme","account"]
        extra_kwargs = {
            'plateforme': {'required': False},
            'account': {'required': False},
        }

class AssetSerializer(ModelSerializer):
    class Meta:
        model = Asset
        fields = ["name","actual_price","currency","date_price","category","number","company","type","ticker","country","sector"]
        extra_kwargs = {
            "number": {'read_only': True},
        }

class CashAccountSerializer(ModelSerializer):
    class Meta:
        model = CashDetail
        fields = ["bank","account","amount"]


class RealEstateDetailSerializer(ModelSerializer):
    class Meta:
        model = RealEstateDetail
        fields = '__all__'
        extra_kwargs = {
            'adresse': {'required': False},
            'sell_date': {'required': False},
            'sell_price': {'required': False},
            'travaux_value': {'required': False},
            'other_costs': {'required': False},
            'notaire_costs': {'required': False},
            'apport': {'required': False},
            'destination': {'required': False},
            'type_rent': {'required': False},
            'defisc': {'required': False},
            'loyer_annuel': {'required': False},
            'charges_annuel': {'required': False},
            'Taxe': {'required': False},
            'rate': {'required': False},
            'duration': {'required': False},
            'part_own': {'required': False},
            'realestate': {'required': False},
            'type_own': {'required': False},
            'emprunt_costs': {'required': False},
        }
    def update(self, instance, validated_data):
        # Retire ces champs de validated_data pour les ignorer
        validated_data.pop('actual_value', None)  # None évite les erreurs si la clé est absente
        validated_data.pop('resteApayer', None)
        
        # Convertir les champs datetime en date si nécessaire
        for attr, value in validated_data.items():
            if isinstance(value, datetime):
                value = value.date()  # Conversion de datetime en date
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class WalletSerializer(ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['amount', 'date']
        extra_kwargs = {
            'amount': {'read_only': True},
            'date': {'read_only': True},
        }          
class CryptoCategorieSerializerDetail(ModelSerializer):
    class Meta:
        model = Crypto
        fields = '__all__'
        read_only_fields = ['wallet','amount','date','type','amount_btc','amount_eth','amount_nft','amount_stablecoins','amount_altcoins']

class BourseCategorieSerializerDetail(ModelSerializer):
    class Meta:
        model = Bourse
        fields = '__all__'
        read_only_fields = ['wallet','amount','date','type','amount_action','amount_etf','amount_forex','amount_obligation','amount_matieres_premieres']

class CashCategorieSerializerDetail(ModelSerializer):
    class Meta:
        model = Cash
        fields = '__all__'
        read_only_fields = ['wallet','amount','date','type','amount_pea','amount_cto','amount_Ass_Vie','amount_CSL_LEP','amount_CC','amount_Livret_A','amount_autre']

class BuyHistoriqueSerializer(ModelSerializer):
    class Meta:
        model=Buy
        fields=["currency","name","number_buy","price_buy","date_buy","ticker"]
        read_only_fields = ["currency","name","number_buy","price_buy","date_buy","ticker"]

class SellHistoriqueSerializer(ModelSerializer):
    class Meta:
        model = Sells
        fields = ["name","ticker","currency","number_sold","price_sold","date_sold"]
        read_only_fields = ["name","ticker","currency","number_sold","price_sold","date_sold"]

class RealEstateHistoriqueSerializer(ModelSerializer):
    class Meta:
        model = RealEstateDetail
        fields = ['buy_date','buy_price','sell_date','sell_price','adresse','destination','emprunt_costs','resteApayer']
        read_only_fields = ['buy_date','buy_price','sell_date','sell_price','adresse','destination','emprunt_costs','resteApayer']

class RevenuAnnuelImmoSerializer(ModelSerializer):
    class Meta:
        model = RealEstateDetail
        fields = ['loyer_annuel','adresse','charges_annuel','Taxe','duration','emprunt_costs']
        read_only_fields = ['loyer_annuel','adresse','charges_annuel','Taxe','duration','emprunt_costs']

class HistoriqueSerializer(ModelSerializer):
    class Meta:
        model = HistoricalPrice
        fields = '__all__'
        read_only_fields = tuple(HistoricalPrice._meta.get_fields())

class HistoriqueWalletSerializer(ModelSerializer):
    class Meta:
        model = HistoricalWallet
        fields = '__all__'
        read_only_fields = tuple(HistoricalPrice._meta.get_fields())

class HistoriqueCashSerializer(ModelSerializer):
    class Meta:
        model = HistoricalCash
        fields = '__all__'
        read_only_fields = tuple(HistoricalPrice._meta.get_fields())

class HistoriqueCryptoSerializer(ModelSerializer):
    class Meta:
        model = HistoricalCrypto
        fields = '__all__'
        read_only_fields = tuple(HistoricalPrice._meta.get_fields())

class HistoriqueBourseSerializer(ModelSerializer):
    class Meta:
        model = HistoricalBourse
        fields = '__all__'
        read_only_fields = tuple(HistoricalPrice._meta.get_fields())

class HistoriqueImmoSerializer(ModelSerializer):
    class Meta:
        model = HistoricalImmo
        fields = '__all__'
        read_only_fields = tuple(HistoricalPrice._meta.get_fields())
