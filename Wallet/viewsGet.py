from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from Wallet.models import Buy, Sells, Wallet, Asset, CryptoDetail, BourseDetail, Cash, CashDetail, Categories, RealEstate, RealEstateDetail, HistoricalPrice,HistoricalWallet, HistoricalCrypto,HistoricalBourse,HistoricalCash,HistoricalImmo, Crypto, Bourse, Cash
from General.models import Asset as AssetGeneral
from General.models import OneYearValue,OldValue
from General.serializers import OneYearValueSerializer,OldValueSerializer
from Wallet.serializers import BuySerializer, CryptoDetailSerializer, BourseDetailSerializer, CashDetailSerializer, SellSerializer, AssetSerializer, CashAccountSerializer, RealEstateDetailSerializer, CryptoCategorieSerializerDetail, BourseCategorieSerializerDetail, CashCategorieSerializerDetail, WalletSerializer, BuyHistoriqueSerializer, SellHistoriqueSerializer, RealEstateHistoriqueSerializer,RevenuAnnuelImmoSerializer, HistoriqueSerializer,HistoriqueWalletSerializer, HistoriqueCashSerializer, HistoriqueBourseSerializer, HistoriqueCryptoSerializer, HistoriqueImmoSerializer,HistoricalPriceSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics, views, status
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.permissions import IsAuthenticated, AllowAny
from datetime import timedelta


class AmountCategories(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        wallet = Wallet.objects.get(user=request.user)
        #on récupère la catégorie souhaité 
        categorie = self.kwargs.get('categorie')
        if categorie in ['crypto','bourse','cash','all']:
            try:
                match categorie:
                    case 'crypto':
                        amounts = Crypto.objects.filter(wallet=wallet, type='Crypto').first()
                        if amounts is None:
                            return Response({"error": "Crypto instance non trouvée"}, status=status.HTTP_404_NOT_FOUND)
                        serializer = CryptoCategorieSerializerDetail(amounts)
                    case 'bourse':
                        amounts = Bourse.objects.filter(wallet=wallet, type='Bourse').first()
                        if amounts is None:
                            return Response({"error": "Bourse instance non trouvée"}, status=status.HTTP_404_NOT_FOUND)
                        serializer = BourseCategorieSerializerDetail(amounts)
                    case 'cash':
                        amounts = Cash.objects.filter(wallet=wallet, type='Cash').first()
                        if amounts is None:
                            return Response({"error": "Cash instance non trouvée"}, status=status.HTTP_404_NOT_FOUND)
                        serializer = CashCategorieSerializerDetail(amounts)
                    case 'all':
                        amounts = Wallet.objects.filter(user=request.user).first()
                        if amounts is None:
                            return Response({"error": "Wallet instance non trouvée"}, status=status.HTTP_404_NOT_FOUND)
                        serializer = WalletSerializer(amounts)

            except Exception as e:
                return Response({"error": f"Erreur inattendue : {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Catégorie invalide
        return Response({"error": "Catégorie invalide"}, status=status.HTTP_400_BAD_REQUEST)
        
class ListAsset(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        wallet = Wallet.objects.get(user=request.user)
        categorie = self.kwargs.get('categorie') #Peut être Bourse Crypto Cash ou Immo
        results = []
        if categorie in ['crypto','bourse']:
            if categorie == 'crypto':
                categorie = 'Crypto'
            else:
                categorie = 'Bourse'
            assets = Asset.objects.filter(category=categorie, wallet=wallet)
            for asset in assets:
                asset.get_new_price()
                #moyenne d'achat
                amount_buy=0
                number_buy=0
                buys = Buy.objects.filter(wallet=wallet,ticker=asset.ticker)
                for buy in buys:
                    amount_buy += buy.price_buy
                    number_buy += buy.number_buy
                average_buy = amount_buy/number_buy
                #moyenne vendu
                amount_sell=0
                number_sell=0
                sells = Sells.objects.filter(wallet=wallet,ticker=asset.ticker)
                for sell in sells:
                    amount_sell += sell.price_sold
                    number_sell += sell.number_sold
                average_sell = amount_sell/number_sell
                #Perf réalisée
                perf_achieved = 0
                for sell in sells:
                    amount_buy_s=0
                    number_buy_s=0
                    for buy in buys:
                        #si l'achat s'est fait avant cette vente
                        if buy.date_buy<=sell.date_sold:
                            amount_buy_s += buy.price_buy
                            number_buy_s += buy.number_buy
                    average_buy_s = amount_buy_s/number_buy_s
                    perf_achieved += ((sell.price_sold/sell.number_sold) - average_buy_s)* sell.number_sold
                #Perf non-réalisée
                asset_hold = asset.number
                perf_unrealized = (asset.actual_price * asset_hold)-(average_buy*asset_hold)
                
                #Type 
                Detail = None
                if categorie == 'crypto' and CryptoDetail.objects.filter(asset = asset).exists():
                    Detail = CryptoDetail.objects.get(asset = asset)
                elif BourseDetail.objects.filter(asset = asset).exists():
                    Detail = BourseDetail.objects.get(asset = asset)
                #données de l'asset retournée 
                asset_data = {
                'id':asset.id,
                'ticker': asset.ticker,
                'average_buy': average_buy,
                'average_sell': average_sell,
                'perf_achieved': perf_achieved,
                'perf_unrealized': perf_unrealized,
                'actual_price': asset.actual_price,
                'asset_hold': asset_hold,
                'nomber_buy':number_buy,
                'number_sell':number_sell,
                'type':[Detail.sous_category if Detail else None],
                }

                results.append(asset_data)
        elif categorie == 'cash':
            Cashs = CashDetail.objects.filter(wallet = wallet)
            for cash in Cashs:
                asset_data = {
                'id':cash.id,
                'bank': cash.bank,
                'account': cash.account,
                'amount': cash.amount,
                }
                results.append(asset_data)
        elif categorie == 'immo':
            realestate = RealEstate.objects.get(wallet=wallet)
            Immos = RealEstateDetail.objects.filter(realestate=realestate)
            for immo in Immos:
                asset_data = {
                'id':immo.id,
                'type': immo.type,
                'adresse': immo.adresse,
                'buy_date': immo.buy_date,
                'buy_price': immo.buy_price,
                'sell_date':immo.sell_date,
                'sell_price':immo.sell_price,
                'destination':immo.destination,
                'actual_value':immo.actual_value,
                }
                results.append(asset_data)
        return Response(results, status=status.HTTP_200_OK)
    

class ListActifPassif(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        wallet = Wallet.objects.get(user=request.user)
        #on vérifie si c'est pour catégorie ou Immo
        categorie = self.kwargs.get('categorie')
        if categorie in ['immo','all']:
            immo = RealEstate.objects.get(wallet=wallet)
            passifs = RealEstateDetail.objects.filter(realestate=immo)
            actifsimmo = RealEstateDetail.objects.filter(realestate=immo)
        else :
            return Response(status=status.HTTP_400_BAD_REQUEST)
        emprunt=0
        for passif in passifs:
            emprunt+=passif.resteApayer
        
        data = {
            'passif':{
                'emprunt':emprunt,
            },
            'actif':{

            },
            'total':0,
        }
        somme_actif=0
        if categorie == 'all':
            data['actif']={
                'Crypto' :  Crypto.objects.filter(wallet=wallet).first().amount,
                'Bourse' :  Bourse.objects.filter(wallet=wallet).first().amount,
                'Cash' :  Cash.objects.filter(wallet=wallet).first().amount,
                'Immo' : RealEstate.objects.filter(wallet=wallet).first().amount,
            }
            somme_actif = wallet.amount
        else:
            for actif in actifsimmo:
                somme_actif+=actif.actual_value
                data['actif'][actif.adresse]=actif.actual_value
            somme_actif-=emprunt
        data['total']=somme_actif
        return Response(data, status=status.HTTP_200_OK)
    

class historiqueAchatVente(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        wallet = Wallet.objects.get(user=request.user)
        categorie = self.kwargs.get('categorie')

        if categorie in ['crypto', 'bourse', 'immo', 'all']:
            try:
                match categorie:
                    case 'crypto':
                        assets = Asset.objects.filter(wallet=wallet, category='Crypto')
                    case 'bourse':
                        assets = Asset.objects.filter(wallet=wallet, category='Bourse')
                    case 'immo':
                        immo = RealEstate.objects.filter(wallet=wallet)
                        amounts = RealEstateDetail.objects.filter(realestate__in=immo)
                        serializer = RealEstateHistoriqueSerializer(instance=amounts, many=True)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    case 'all':
                        assets = Asset.objects.filter(wallet=wallet)
                    case _:
                        return Response({"error": "Catégorie non reconnue"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": "Instance non trouvée"}, status=status.HTTP_404_NOT_FOUND)

            # Gestion des actifs (Crypto et Bourse et all)
            data = []
            for asset in assets:
                buys = Buy.objects.filter(ticker=asset.ticker, wallet=wallet)
                sells = Sells.objects.filter(ticker=asset.ticker, wallet=wallet)
                serializer_buy = BuyHistoriqueSerializer(instance=buys, many=True)
                serializer_sell = SellHistoriqueSerializer(instance=sells, many=True)

                data.append({
                    "asset": asset.name,
                    "achats": serializer_buy.data,
                    "ventes": serializer_sell.data,
                })

            return Response(data, status=status.HTTP_200_OK)

        return Response({"error": "Catégorie invalide"}, status=status.HTTP_400_BAD_REQUEST)

class RevenuAnnuelImmo(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        wallet = Wallet.objects.get(user=request.user)
        immoGeneral = RealEstate.objects.filter(wallet=wallet)
        immos = RealEstateDetail.objects.filter(realestate__in=immoGeneral)
        serializer = RevenuAnnuelImmoSerializer(instance = immos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MomentumPF(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        wallet = Wallet.objects.get(user=request.user)
        #on récupère la catégorie souhaité 
        amounts=None
        categorie = self.kwargs.get('categorie')
        if categorie in ['crypto','bourse','all']:
            match categorie:
                case 'crypto':
                    amounts = Asset.objects.filter(wallet=wallet, category='Crypto')
                case 'bourse':
                    amounts = Asset.objects.filter(wallet=wallet, category='Bourse')
                case 'all':
                    amounts = Asset.objects.filter(wallet=wallet)
        #si aucun asset ou si la catégorie saisie est mauvaise
        if amounts==None:
            return Response({"error": "Instance non trouvée"}, status=status.HTTP_404_NOT_FOUND)
        #on va iterer les assets et venir récupérer la perf sur 1 3 et 6 mois.
        data = []
        for amount in amounts:
            amount.get_new_price()
            if AssetGeneral.objects.filter(ticker=amount.ticker).exists():
                assetG = AssetGeneral.objects.get(ticker=amount.ticker)
                print(assetG)
            else:
                count = 0
                #Ici on fera un momentum avec les donnée historique
                Vactuelle = amount.actual_price
                lastDate = amount.date_price
                #1 mois
                target_date = lastDate - timedelta(days=30)
                try : 
                    count +=1
                    oneYearV = HistoricalPrice.objects.filter(asset=amount, date__lte=target_date).order_by('-date').first()
                    OneMonth = ((Vactuelle-oneYearV.value)/Vactuelle)*100
                except HistoricalPrice.DoesNotExist:
                    count -= 1
                    OneMonth = 0
                #3 mois
                target_date = lastDate - timedelta(days=90)
                try : 
                    count +=1
                    oneYearV = HistoricalPrice.objects.filter(asset=amount, date__lte=target_date).order_by('-date').first()
                    ThreeMonth = ((Vactuelle-oneYearV.value)/Vactuelle)*100
                except HistoricalPrice.DoesNotExist:
                    count -= 1
                    ThreeMonth = 0
                #6 mois
                target_date = lastDate - timedelta(days=180)
                try : 
                    count +=1
                    oneYearV = HistoricalPrice.objects.filter(asset=amount, date__lte=target_date).order_by('-date').first()
                    SixMonth = ((Vactuelle-oneYearV.value)/Vactuelle)*100
                except HistoricalPrice.DoesNotExist:
                    count -= 1
                    SixMonth = 0
                #Average 
                if count>0:
                    Increase = (OneMonth+ThreeMonth+SixMonth)/count
                else : 
                    Increase = 0
                data.append({
                'ticker':amount.ticker,
                'name':amount.name,
                'value':Increase,
                })
                continue
            assetG.maj_asset()
            #valeur actuelle : 
            Vactuelle = assetG.last_value
            lastDate = assetG.date_value
            #valeur du mois dernier :
            target_date = lastDate - timedelta(days=30)
            print( OneYearValue.objects.filter(asset=assetG))
            oneYearV = OneYearValue.objects.filter(asset=assetG, date__lte=target_date).order_by('-date').first()
            OneMonth = ((Vactuelle-oneYearV.value)/Vactuelle)*100
            #valeur de 3 mois
            target_date_3 = lastDate - timedelta(days=90)
            oneYearV_3 = OneYearValue.objects.filter(asset=assetG, date__lte=target_date_3).order_by('-date').first()
            ThreeMonth = ((Vactuelle-oneYearV_3.value)/Vactuelle)*100
            #valeur de 6 mois
            target_date_6 = lastDate - timedelta(days=180)
            oneYearV_6 = OneYearValue.objects.filter(asset=assetG, date__lte=target_date_6).order_by('-date').first()
            SixMonth = ((Vactuelle-oneYearV_6.value)/Vactuelle)*100
            #moyenne 
            Increase = (OneMonth+ThreeMonth+SixMonth)/3
            data.append({
                'ticker':amount.ticker,
                'name':amount.name,
                'value':Increase,
            })
        return Response(data, status=status.HTTP_200_OK)

#permet de récupérer toutes les données propre à un Asset (Crypto, Bourse, Immo, Cash)
class AssetData(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        def getHistoricalPriceAPI(ticker):
            assetG = AssetGeneral.objects.get(ticker=ticker)
            oneYearValues = OneYearValue.objects.filter(asset=assetG).order_by('date')
            serializerOneYears = OneYearValueSerializer(instance=oneYearValues, many=True)
            oldValues = OldValue.objects.filter(asset=assetG).order_by('date')
            serializerOldValues = OldValueSerializer(instance=oldValues, many=True)

            oneYearPerf = None
            fiveYearPerf = None
            tenYearPerf = None

            if oneYearValues.exists():
                first_value = oneYearValues[0].value
                if first_value:
                    oneYearPerf = ((assetG.last_value - first_value) / first_value) * 100

            lastDate = assetG.date_value
            if lastDate:
                target_date = lastDate - timedelta(days=1820)
                oldValue = OldValue.objects.filter(asset=assetG, date__lte=target_date).order_by('-date').first()
                if oldValue and oldValue.value:
                    fiveYearPerf = ((assetG.last_value - oldValue.value) / oldValue.value) * 100

                target_date = lastDate - timedelta(days=3645)
                oldValue = OldValue.objects.filter(asset=assetG, date__lte=target_date).order_by('-date').first()
                if oldValue and oldValue.value:
                    tenYearPerf = ((assetG.last_value - oldValue.value) / oldValue.value) * 100

            data = {
                'oneYearValues': serializerOneYears.data,
                'oldValues': serializerOldValues.data,
                'oneYearPerf': oneYearPerf,
                'fiveYearPerf': fiveYearPerf,
                'tenYearPerf': tenYearPerf,
            }
            return data

        def getHistoricalPrice(ForeignKey, data):
            match ForeignKey:
                case 'asset':
                    historiques = HistoricalPrice.objects.filter(asset=data)
                case 'immo':
                    historiques = HistoricalPrice.objects.filter(RealEstate=data)
                case 'cash':
                    historiques = HistoricalPrice.objects.filter(cash=data)
            serializer = HistoricalPriceSerializer(instance=historiques, many=True)
            return serializer.data

        wallet = Wallet.objects.get(user=request.user)
        categorie = self.kwargs.get('categorie')
        id = self.kwargs.get('pk')

        if categorie == 'bourse' or categorie == 'crypto':
            asset = Asset.objects.get(id=id)
            asset.get_new_price()
            serializerAsset = AssetSerializer(instance=asset)

            if categorie == 'bourse':
                if BourseDetail.objects.filter(asset=asset).exists():
                    detail = BourseDetail.objects.get(asset=asset)
                    serializerDetail = BourseDetailSerializer(instance=detail)
                else:
                    serializerDetail=None
            else:
                if CryptoDetail.objects.filter(asset=asset).exists():
                    detail = CryptoDetail.objects.get(asset=asset)
                    serializerDetail = CryptoDetailSerializer(instance=detail)
                else:
                    serializerDetail=None

            buys = Buy.objects.filter(wallet=wallet, ticker=asset.ticker).order_by('date_buy')
            serializerBuy = BuySerializer(instance=buys, many=True)
            sells = Sells.objects.filter(wallet=wallet, ticker=asset.ticker).order_by('date_sold')
            serializerSell = SellSerializer(instance=sells, many=True)

            data = {
                'asset': serializerAsset.data,
                'detail':[serializerDetail.data if serializerDetail else None],
                'buys': serializerBuy.data,
                'sells': serializerSell.data,
            }

            if asset.api_know:
                response = getHistoricalPriceAPI(asset.ticker)
            else:
                response = getHistoricalPrice('asset', asset)

            data['historical_data'] = response
            return Response(data, status=status.HTTP_200_OK)

        elif categorie == 'immo':
            immoGeneral = RealEstate.objects.get(wallet=wallet)
            immo = RealEstateDetail.objects.get(realestate=immoGeneral, id=id)
            serializer = RealEstateDetailSerializer(instance=immo)
            historiques = HistoricalPrice.objects.filter(RealEstate=immo)
            serializerHistorique = HistoriqueSerializer(instance=historiques, many=True)

            data = {
                'immo': serializer.data,
                'historique': serializerHistorique.data,
            }
            return Response(data, status=status.HTTP_200_OK)

        elif categorie == 'cash':
            cash = CashDetail.objects.get(wallet=wallet, id=id)
            serializer = CashAccountSerializer(instance=cash)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Gestion du cas imprévu
        return Response(
            {"error": f"Invalid category '{categorie}' provided."},
            status=status.HTTP_400_BAD_REQUEST
        )

        

#donne les historiques de prix soit All, soit Crypto, Bourse, Cash ou Immo  
class PerformanceGlobal(APIView):
    permission_classes = (IsAuthenticated,)
    #la somme en cash sera calculé sur la valeur du portefeuille depuis la date d'aujourd'hui
    def get(self, request, *args, **kwargs):
        wallet = Wallet.objects.get(user=request.user)
        #on récupère la catégorie souhaité et l'id All, Crypto, Bourse, Cash ou Immo 
        categorie = self.kwargs.get('categorie')
        data = []
        match categorie:
            case 'all':
                datas= HistoricalWallet.objects.filter(wallet=wallet).order_by('-date')
                print(f"len datas get in view ===== {len(datas)}")
                print(f" datas get in view ===== {datas}")
                datas = HistoriqueWalletSerializer(instance = datas, many=True)
            case 'crypto':
                datas= HistoricalCrypto.objects.filter(wallet=wallet).order_by('-date')
                datas = HistoriqueCryptoSerializer(instance = datas, many=True)
            case 'bourse':
                datas =HistoricalBourse.objects.filter(wallet=wallet).order_by('-date')
                datas = HistoriqueBourseSerializer(instance = datas, many=True)
            case 'cash':
                datas =HistoricalCash.objects.filter(wallet=wallet).order_by('-date')
                datas = HistoriqueCashSerializer(instance = datas, many=True)
            case 'immo':
                datas =HistoricalImmo.objects.filter(wallet=wallet).order_by('-date')
                datas = HistoriqueImmoSerializer(instance = datas, many=True)
        return Response(datas.data, status=status.HTTP_200_OK)
