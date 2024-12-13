from datetime import date, timedelta
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from API.Wallet.models import Buy, Sells, Wallet, Asset, CryptoDetail, BourseDetail, Cash, CashDetail, Categories, RealEstate, RealEstateDetail, HistoricalWallet, Bourse, Crypto
from API.General.models import Asset as AssetGeneral
from API.General.models import OneYearValue, OldValue
from API.Wallet.serializers import BuySerializer, CryptoDetailSerializer, BourseDetailSerializer, CashDetailSerializer, SellSerializer, AssetSerializer, CashAccountSerializer, RealEstateDetailSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics, views, status
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.shortcuts import get_object_or_404
# Create your views here.

#créer une requête avec chatgpt pour avoir les informations et le dernier prix d'un asset qui n'est pas donné par yfinance
#si l'user enregistre un nouveau asset à son wallet qui est non suivie qui est bourse ou crypto, alors une requete est envoyé à chatgpt pour me donner les réponses


# historique detail :  Il me faut une vue qui vient récupérer les buy et sell d'une valeur d'actif puis récupérer la nombre d'action sur ces valeur, fait le calcul et retour une dict d'array avec la valeur en currency de cet actif
# historique en list : 
    # - soit sur crypto 
    # - soit sur bourse 
    # - spot sur immo

# On doit aussi faire les vues de get lorsqu'il veut acheter autofill du questionnaire si déjà un asset ou via general
# get all data 
#...

#A voir pour faire des fonction sur les serializer qui sont tout le temps similaire (cash nottament)
class BuyView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, format=None):
        wallet = Wallet.objects.get(user=request.user)
        #Création du Buy
        try :
            serializer = BuySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(wallet = wallet)
            else:
                return Response({"error": "Données invalides", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error":f"L'achat n'a pas pu être enregistré : {e}"}, status=status.HTTP_400_BAD_REQUEST)
        #On récupère les données transmises
        data = request.data
        #on vérifie qu'un asset n'est pas déjà existant : 
        buy = Buy.objects.filter(date_buy = data.get("date_buy"), wallet=wallet, ticker=data.get("ticker")).first()
        asset = Asset.objects.filter(wallet=wallet, ticker=data.get("ticker")).first()
        #s'il n'y a pas déjà un asset 
        if asset == None: 
            #Si l'API est connue
            assetG = AssetGeneral.objects.filter(ticker=data.get("ticker")).first()
            if not assetG:
                response = AssetGeneral.create_asset(self,data.get("ticker"))
                if response != True: 
                    if "type" in data and "categories" in data and "country" in data and "sector" in data and "company" in data:
                        buy.new_buy(data.get('type'), data.get('categories'), data.get('country'), data.get('sector'), data.get('company'))
                    else:
                        return Response({"error":"Vous devez renseignez les éléments suivants sur l'actif : Type;Categories;Pays;Secteur;Entreprise"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    buy.new_buy()
            else:
                buy.new_buy()
        else:
            buy.new_buy()
        if  AssetGeneral.objects.filter(ticker=data.get("ticker")).exists():
            OneYearValue.create_OneYearValue(self,data.get("ticker"))
            OldValue.create_OldValue(self,data.get("ticker") )
        #Gestion des Bourse et CashDetail
        if "cryptoDetail" in data:
            try:
                #On vérifie s'il on doit créer ou mettre à jour
                cryptoDetail = CryptoDetail.objects.filter(asset=asset, wallet=wallet).first()
                if cryptoDetail :
                    serializerCash = CryptoDetailSerializer(cryptoDetail, data=data.get("cryptoDetail"), partial=True)
                else : 
                    serializerCash = CryptoDetailSerializer(data = data.get("cryptoDetail"))
                if serializerCash.is_valid():
                    serializerCash.save(wallet=wallet, asset=asset)
                crypto = Crypto.objects.get(wallet=wallet)
                crypto.maj_SubWallet(crypto.type)
            except Exception as e:
                return Response({"error":f"La création de CryptoDetail n'a pas pu se faire : {e}"}, status=status.HTTP_400_BAD_REQUEST)
        elif "bourseDetail" in data:
            try:
                bourseDetail = BourseDetail.objects.filter(asset=asset, wallet=wallet).first()
                if bourseDetail:
                    serializerCash = BourseDetailSerializer(bourseDetail, data=request.data("bourseDetail"), partial=True)
                else :
                    serializerCash = BourseDetailSerializer(data = request.data("bourseDetail"))
                if serializerCash.is_valid():
                    serializerCash.save(wallet=wallet, asset=asset)
                bourse = Bourse.objects.get(wallet=wallet)
                bourse.maj_SubWallet(bourse.type)
            except Exception as e:
                return Response({"error":f"La création de BourseDetail n'a pas pu se faire:{e}"}, status=status.HTTP_400_BAD_REQUEST)
        #Gestion de CashDetail
        if "cashDetail" in data: 
            data = data.get("cashDetail")
            try:
                cashDetail = CashDetail.objects.get(wallet=wallet, account=data.get("account"), bank=data.get("bank"))
                if cashDetail :
                    cashDetail.cash_maj_Amount(data.get("amount"))
                else : 
                    serializerCash = CashDetailSerializer(data=data)
                    if serializerCash.is_valid():
                        serializerCash.save(wallet = wallet)
                cash = Cash.objects.get(wallet=wallet)
                cash.maj_Cash()
            except Exception as e:
                return Response({"error":f"La mise à jour du Cash n'a pas pu se faire: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
#Il est préférable de faire une vente plutôt qu'une suppression car ca ne retourne pas le cash et initialise pas asset ni les montants
class DeleteBuyView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        wallet = Wallet.objects.get(user=request.user)
        id = self.kwargs.get('pk')
        if Buy.objects.filter(wallet=wallet, id=id).exists():
            buy = Buy.objects.get(wallet=wallet, id=id)
            buy.delete()

            return Response({"success": "L'achat a été supprimé avec succès."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error":"L'instance de buy est introuvable"},status=status.HTTP_400_BAD_REQUEST)

class SellView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, format=None):
        wallet = Wallet.objects.get(user=request.user)
        #Création du Buy
        try :
            serializer = SellSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save(wallet = wallet)
            else : 
                return Response({"error": "Données invalides", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error":f"La vente n'a pas pu être enregistrée : {e}"}, status=status.HTTP_400_BAD_REQUEST)
        #On récupère les données transmises
        data = request.data
        #on vérifie qu'un asset n'est pas déjà existant : 
        sell = Sells.objects.filter(date_sold = data.get("date_sold"), wallet=wallet, ticker=data.get("ticker")).first()
        asset = Asset.objects.filter(wallet=wallet, ticker=data.get("ticker")).first()
        #s'il n'y a pas déjà un asset 
        if not asset : 
            assetG = AssetGeneral.objects.filter(ticker=data.get("ticker")).first()
            if not assetG:
                if "type" in data and "categories" in data and "country" in data and "sector" in data and "company" in data:
                    sell.new_sell(data.get('type'), data.get('categories'), data.get('country'), data.get('sector'), data.get('company'))
                else:
                    return Response({"error":"Vous devez renseignez les éléments suivants sur l'actif : Type;Categories;Pays;Secteur;Entreprise"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                sell.new_sell()
        else:
            sell.new_sell()
        #Gestion de CashDetail
        if "cashDetail" in data: 
            data = data.get("cashDetail")
            try:
                cashDetail = CashDetail.objects.get(wallet=wallet, account=data.get("account"), bank=data.get("bank"))
                if cashDetail :
                    cashDetail.cash_maj_Amount(data.get("amount"))
                else : 
                    serializerCash = CashDetailSerializer(data=data)
                    if serializerCash.is_valid():
                        serializerCash.save(wallet = wallet)
                cash = Cash.objects.get(wallet=wallet)
                cash.maj_Cash()
            except Exception as e:
                return Response({"error":f"La mise à jour du Cash n'a pas pu se faire {e}"}, status=status.HTTP_400_BAD_REQUEST)
        crypto = Crypto.objects.get(wallet=wallet)
        crypto.maj_SubWallet(crypto.type)
        bourse = Bourse.objects.get(wallet=wallet)
        bourse.maj_SubWallet(bourse.type)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
#Il est préférable de faire un achat plutôt qu'une suppression car ca ne retourne pas le cash et initialise pas asset ni les montants
class DeleteSellView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        wallet = Wallet.objects.get(user=request.user)
        id = self.kwargs.get('pk')
        if Sells.objects.filter( wallet=wallet, id=id).exists():
            sell = Sells.objects.get(wallet=wallet, id=id)
            sell.delete()
            return Response({"success": "La vente a été supprimée avec succès."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "L'instance de sell est introuvable"},status=status.HTTP_400_BAD_REQUEST)

#Pour mettre à jour les données de Crypto et Bourse
class MajAsset(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request, format=None):
        wallet = Wallet.objects.get(user=request.user)
        if Asset.objects.filter(wallet=wallet, ticker=request.data.get('ticker')).exists():
            asset = Asset.objects.get(wallet=wallet, ticker=request.data.get('ticker'))
        else : 
            return Response({"error":"Aucun asset ne correspond"}, status=status.HTTP_404_NOT_FOUND)
        data = request.data
        
        #on gère d'abord la gestion des historiques
        if not asset.api_know and (data.get('actual_price') or data.get('number')):
            price = data.get('actual_price')
            number = data.get('number')
            asset.maj_asset_withoutAPI(price, number)
        #on met à jour 
        serializer = AssetSerializer(asset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(wallet=wallet)
            #On remet à jour les sommes des catégories:
            if asset.category == 'Crypto':
                categories = Crypto.objects.get(wallet=wallet)
            else:
                categories = Bourse.objects.get(wallet=wallet)
        categories.maj_SubWallet(asset.category)
        if "cryptoDetail" in data:
            try:
                #On vérifie s'il on doit créer ou mettre à jour
                cryptoDetail = CryptoDetail.objects.filter(asset=asset, wallet=wallet).first()
                if cryptoDetail :
                    serializerCash = CryptoDetailSerializer(cryptoDetail, data=data.get("cryptoDetail"), partial=True)
                else : 
                    serializerCash = CryptoDetailSerializer(data = data.get("cryptoDetail"))
                if serializerCash.is_valid():
                    serializerCash.save(wallet=wallet, asset=asset)
            except Exception as e:
                return Response({"error":f"La création de CryptoDetail n'a pas pu se faire : {e}"}, status=status.HTTP_400_BAD_REQUEST)
        elif "bourseDetail" in data:
            try:
                bourseDetail = BourseDetail.objects.filter(asset=asset, wallet=wallet).first()
                if bourseDetail:
                    serializerCash = BourseDetailSerializer(bourseDetail, data=request.data("bourseDetail"), partial=True)
                else :
                    serializerCash = BourseDetailSerializer(data = request.data("bourseDetail"))
                if serializerCash.is_valid():
                    serializerCash.save(wallet=wallet, asset=asset)
            except Exception as e:
                return Response({"error":f"La création de BourseDetail n'a pas pu se faire:{e}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)
        
#Pour créer, supprimer ou modifier ou récupérer
class CashAccount(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CashAccountSerializer

    def get_queryset(self):
        wallet = Wallet.objects.get(user=self.request.user)
        if self.action == "retrieve":
            return CashDetail.objects.get(wallet=wallet, id=self.kwargs.get('pk'))
        return CashDetail.objects.filter(wallet=wallet)
    
    def perform_create(self, serializer):
        wallet = Wallet.objects.get(user=self.request.user)
        HistoricalWallet.NewValue('Cash',timezone.now(),self.request.data.get('amount'),0,0,wallet)
        serializer = self.get_serializer(data=self.request.data)
        if serializer.is_valid():
            serializer.save(wallet=wallet)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"detail":"Les données transmisses sont incorrectes"},status=status.HTTP_400_BAD_REQUEST)
        
    
    def perform_update(self, serializer):
        #on vérifie d'abord que c'est la donnée addremove qui est envoyé alors on fera que une transaction atomique 
        wallet = Wallet.objects.get(user=self.request.user)
        id = self.kwargs.get("pk")
        cashDetail = CashDetail.objects.get(wallet=wallet,id=id)
        if "addremove" in self.request.data :
            cashDetail.cash_maj_Amount(amount=self.request.data.get("addremove"))
            return Response(status=status.HTTP_200_OK)
        # sinon on met le serializer à jour car c'esr le montant qui est direct modifié 
        # on met d'abord a jour HistoricalWallet
        HistoricalWallet.NewPrice('Cash',timezone.now(),cashDetail.amount-self.request.data.get("amount"), wallet)
        serializer = self.get_serializer(cashDetail,data=self.request.data ,partial=True)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
    
class RealEstateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        wallet = Wallet.objects.get(user=request.user)
        #Création de real estate detail si besoin
        if  RealEstate.objects.filter(wallet=wallet).exists():
            realestate = RealEstate.objects.get(wallet=wallet)
        else :
            realestate = RealEstate.objects.create(wallet=wallet, amount=0)
        #Création du Buy
        serializer = RealEstateDetailSerializer(data = request.data)
        if serializer.is_valid():
            print("passage ici")
            serializer.save(realestate = realestate)
            HistoricalWallet.NewValue('Immo',request.data.get('buy_date'),request.data.get('actual_value')-request.data.get('resteApayer'),serializer.instance,0,wallet)
        else: 
            return Response({"error":f"Impossible d'enregristrer les données {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
        realestate.maj_amount()
        #Gestion de CashDetail
        if "cashDetail" in request.data: 
            data = request.data.get("cashDetail")
            try:
                cashDetail = CashDetail.objects.get(wallet=wallet, account=data.get("account"), bank=data.get("bank"))
                if cashDetail :
                    cashDetail.cash_maj_Amount(data.get("amount"))
                else : 
                    serializerCash = CashDetailSerializer(data=data)
                    if serializerCash.is_valid():
                        serializerCash.save(wallet = wallet)
                        HistoricalWallet.NewValue('Cash',request.data.get('buy_date'),(request.data.get('apport')*-1),serializerCash.instance,0,wallet)
            except Exception as e:
                return Response({"error":f"La mise à jour du Cash n'a pas pu se faire {e}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    #dans patch les valeur actual_value et resteApayer sont envoyée elles seront traitée par la transaction atomique et le reste via le serializer
    def patch(self, request, *args, **kwargs):
        wallet = Wallet.objects.get(user=request.user)
        realestate = RealEstate.objects.get(wallet=wallet)
        realestatedetail = RealEstateDetail.objects.get(realestate=realestate,id=self.kwargs.get('pk'))
        #Création du Buy
        actual_value='undifined'
        resteApayer='undifined'
        if 'actual_value' in request.data:
            actual_value=request.data.get('actual_value')
        if 'resteApayer' in request.data:
            resteApayer=request.data.get('resteApayer')
        try :
            realestatedetail.maj_realEstateDetail(actual_value, resteApayer)
            serializer = RealEstateDetailSerializer(realestatedetail,data=request.data ,partial=True)
            if serializer.is_valid():
                serializer.save()
        except Exception as e:
            return Response({"error":f"Impossible de mettre à jour les données : {e}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)
    



    

    
