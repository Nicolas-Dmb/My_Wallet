import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Asset, Buy, Sells, Wallet, CryptoDetail, BourseDetail, CashDetail, RealEstate, RealEstateDetail, HistoricalPrice, HistoricalWallet, HistoricalCrypto, HistoricalBourse, HistoricalCash, HistoricalImmo, Bourse, Crypto
import django
from User.tests import register_user, account_fixture, user_token
django.setup()

User = get_user_model()

# je n'ai pas tester les historical price et historical wallet

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def buy():#Il faudra ajouter wallet
    return {
        "API_Know":{
            "currency":'EUR',
            "name":"aple",
            "plateforme":"CIC",
            "account":"CT",
            "number_buy":"1",
            "price_buy":"350",
            "date_buy":"2024-07-12",
            "ticker":"AAPL",
        },
        "unKnowErrorData":{
            "currency":"USD",
            "name":"EGLD",
            "plateforme":"MAYAR",
            "account":"",
            "number_buy":"10",
            "price_buy":"200",
            "date_buy":"2023-01-12",
            "ticker":"EGLDkodezj",
        },
        "unKnow":{
            "currency":"USD",
            "name":"EGLD",
            "plateforme":"MAYAR",
            "account":"",
            "number_buy":"10",
            "price_buy":"200",
            "date_buy":"2023-01-12",
            "ticker":"EGLDdejzi",
            "type":"Altcoins",
            "categories":"Crypto",
            "country":"",
            "sector":"",
            "company":"",
        }
    }


@pytest.fixture
def sell():#Il faudra ajouter wallet
    return {
        "API_Know":{
            "currency":'EUR',
            "name":"aple",
            "plateforme":"CIC",
            "account":"CT",
            "number_sold":"1",
            "price_sold":"450",
            "date_sold":"2024-09-10",
            "ticker":"AAPL",
        },
        "unKnow":{
            "currency":"USD",
            "name":"EGLD",
            "plateforme":"MAYAR",
            "account":"",
            "number_sold":"5",
            "price_sold":"100",
            "date_sold":"2024-07-12",
            "ticker":'EGLDdejzi',
        }
    }


@pytest.fixture(params=['API_Know1','unKnow1','unKnow2','unKnow3'])
def modif(request):
    data= {
        "API_Know1":{
            "currency":'EUR',
            "name":"apple",
            "plateforme":"Revolut",
            "account":"CT",
            "ticker":"AAPL",
        },
        "unKnow1":{
            "currency":"USD",
            "name":"EGLD",
            "plateforme":"Xportal",
            "ticker":'EGLDdejzi',
        },
        "unKnow2":{
            "currency":"USD",
            "name":"EGLD1",
            "plateforme":"Xportal",
            "account":"",
            "actual_price":"100",
            "ticker":'EGLDdejzi',
            "category":"Crypto",
        },
        "unKnow3":{ 
            "actual_price":"150",
            "ticker":'EGLDdejzi',
        }
    }
    return data[request.param]

@pytest.fixture
def Newbuy():#Il faudra ajouter wallet
    return {
        "API_Know":{
            "currency":'EUR',
            "name":"apple",
            "plateforme":"CIC",
            "account":"CT",
            "number_buy":"2",
            "price_buy":"400",
            "date_buy":"2024-12-12",
            "ticker":"AAPL",
        },
        "unKnow":{
            "currency":"USD",
            "name":"EGLD",
            "plateforme":"XPortal",
            "account":"",
            "number_buy":"2",
            "price_buy":"100",
            "date_buy":"2023-10-12",
            "ticker":'EGLDdejzi',
        }
    }
@pytest.fixture
def NewRealEstate():# Vérifie que actual value se mette à jour en même temps
    return {
        "Full_data":{
        "type":'Appartement',
        "adresse":"120 rue Jean Jaures, Paris",
        "buy_date":"2020-12-26",
        "buy_price":250000,
        "travaux_value":20000,
        "other_costs":2000,
        "notaire_costs":10000,
        "apport":10000,
        "destination":'RP',
        "type_rent":'Vide',
        "loyer_annuel":10000,
        "charges_annuel":5000,
        "taxe":2000,
        "emprunt_costs":20000,
        "resteApayer":170000,
        "rate":2.2,
        "duration":20,
        "actual_value":250000,
        },
        "Less_data":{
        "type":'Appartement',
        "adresse":"12 rue Jean Jaures, Paris",
        "buy_date":"2020-12-26",
        "buy_price":250000,
        "apport":10000,
        "resteApayer":170000,
        "duration":20,
        "actual_value":250000,
        }
    }
@pytest.fixture
def ModifRealEstate():# Vérifie que actual value se mette à jour en même temps
    return {
        "Full_data":{
        "adresse":"50 rue Jean Jaures, Paris",
        "actual_value":300000,
        },
        "Less_data":{
        "loyer_annuel":10000,
        "charges_annuel":5000,
        "taxe":2000,
        "emprunt_costs":20000,
        "resteApayer":170000,
        "rate":2.2,
        "actual_value":310000,
        "adresse":"12 rue Jean Jaures, Paris",
        }
    }
@pytest.fixture
def NewCashDetail():
    return{
        "LEP":{
            "bank":"Societe Generale",
            "account":"CSL_LEP",
            "amount":10000,
        },
        "PEA":{
            "bank":"BNP",
            "account":"PEA",
            "amount":15000,
        },
        "CTO":{
            "bank":"CA",
            "account":"CTO",
            "amount":2000,
        }
    }
@pytest.fixture
def ModifCashDetail():
    return{
        "LEP":{
            "bank":"Societe Générale",
            "addremove":2000,
        },
        "PEA":{
            "addremove":-1000,
        },
        "CTO":{
            "bank":"CIC",
            "account":"CTO",
            "amount":3000,
        },
    }

@pytest.fixture
def BuyFixture(api_client,buy,register_user,user_token):
     #data à vérifier ensuite 
        user = register_user
        access_token = user_token['access']
        wallet = Wallet.objects.get(user=user)
        url = reverse('buy_asset')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        list = ["API_Know","unKnow","unKnowErrorData"]
        for data in list:
            response = api_client.post(url,buy[data],format='json')
            if data == "unKnow" or data == "API_Know":
                assert response.status_code == 201

@pytest.fixture
def PostSell(api_client,sell,register_user,user_token):
        user = register_user
        access_token = user_token['access']
        wallet = Wallet.objects.filter(user=user)
        url = reverse('sell_asset')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        
        list = ["API_Know","unKnow"]
        for data in list:
            response = api_client.post(url,sell[data],format='json')
            assert response.status_code == 201

@pytest.fixture
def PostCash(api_client,register_user,user_token,NewCashDetail):
        user = register_user
        access_token = user_token['access']
        datas=[]
        url = reverse('cash-list')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        list = ["LEP","PEA","CTO"]
        for accounttype in list:
            response = api_client.post(url, NewCashDetail[accounttype], format='json')
            assert response.status_code == 201
            datas.append(response.data)
        return datas
         

@pytest.fixture
def RealEstateDetailfixture(api_client,NewRealEstate,ModifRealEstate, register_user,user_token):
        user = register_user
        access_token = user_token['access']
        list = ["Full_data","Less_data"]
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        for data in list :
            url = reverse('new_realEstate')
            response = api_client.post(url,NewRealEstate[data],format='json')
            assert response.status_code == 201
            immo = RealEstateDetail.objects.get(adresse=NewRealEstate[data]["adresse"])
            assert immo.actual_value == NewRealEstate[data]["buy_price"]
            #Modif
            url = reverse('maj_realEstate', kwargs={'pk': immo.id})
            response = api_client.patch(url,ModifRealEstate[data],format='json')
            print(response.data)
            assert response.status_code == 200

#Création Buy et Création Sell (API_know)
@pytest.mark.django_db
class TestBuySellAPI:
    #post puis delete 
    def testPostBuy(self,api_client,buy,register_user,user_token):
        user = register_user
        access_token = user_token['access']
        wallet = Wallet.objects.get(user=user)
        url = reverse('buy_asset')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        list = ["API_Know","unKnow","unKnowErrorData"]
        for data in list:
            response = api_client.post(url,buy[data],format='json')
            if data == "unKnow" or data == "API_Know":
                assert response.status_code == 201
                #on vérifie que asset et buy on été créer et que wallet est plus cher qu'avant
                wallet1 = Wallet.objects.get(user=user)
                crypto = Crypto.objects.get(wallet=wallet)
                bourse = Bourse.objects.get(wallet=wallet)
                assert Buy.objects.filter(ticker=buy[data]["ticker"],wallet=wallet).exists()
                assert Asset.objects.filter(ticker=buy[data]["ticker"],wallet=wallet).exists()
                asset = Asset.objects.get(ticker=buy[data]["ticker"],wallet=wallet)
                assert asset.number == float(buy[data]['number_buy'])
                assert wallet1.amount > wallet.amount
            else :
                assert response.status_code == 400
        #On vérifie que les sous catégories ont été créer
        assert Crypto.objects.filter(wallet=wallet).exists()
        assert Bourse.objects.filter(wallet=wallet).exists()
        #Delete
        buy = Buy.objects.get(ticker=buy["API_Know"]["ticker"],wallet=wallet)
        url = reverse('delete_buy', kwargs={'pk': buy.id})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = api_client.delete(url,format='json')
        assert response.status_code == 204
        assert not Buy.objects.filter(id=buy.id,wallet=wallet).exists()
        #ici il n'y a pas d'inilialisation de amount ni de cash etc quand on fait une suppression donc préférable de faire une vente
        #wallet2 = Wallet.objects.get(user=user)
        #assert wallet1.amount > wallet2.amount
    
    #post puis delete 
    def testPostSell(self, api_client,sell,BuyFixture,register_user,user_token,buy):
        user = register_user
        access_token = user_token['access']
        wallet = Wallet.objects.get(user=user)
        #data à vérifier ensuite 
        categoriesAvant = Bourse.objects.get(wallet=wallet)
        categoriesCryptoAvant =  Crypto.objects.get(wallet=wallet)
        assetAAPL = Asset.objects.get(ticker='AAPL',wallet=wallet)
        assetEGLD =  Asset.objects.get(ticker='EGLDdejzi',wallet=wallet)
        
        url = reverse('sell_asset')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        
        list = ["API_Know","unKnow"]
        for data in list:
            response = api_client.post(url,sell[data],format='json')

            assert response.status_code == 201
            print(f"asset apple : {assetAAPL.number}")
            print(f"asset EGLD : {assetEGLD.number}")
            NewAssetApple = Asset.objects.get(ticker="AAPL",wallet=wallet)
            NewAssetEGLD = Asset.objects.get(ticker='EGLDdejzi',wallet=wallet)
            print(f"nouvelle asset Apple : {NewAssetApple.number}")
            print(f"nouvelle asset EGLD : {NewAssetEGLD.number}")
            #on vérifie que asset, categorie et wallet a été créer  
            wallet1 = Wallet.objects.get(user=user)
            print(wallet1)
            assert Buy.objects.filter(ticker=sell[data]["ticker"],wallet=wallet).exists()
            asset = Asset.objects.get(ticker=sell[data]["ticker"],wallet=wallet)
            if data == "unKnow":
                categoriesCryptoAprès = Crypto.objects.get(wallet=wallet, type='Crypto')
                assert categoriesCryptoAprès.amount < categoriesCryptoAvant.amount
                assert asset.number == assetEGLD.number-int(sell[data]['number_sold'])
            else :
                categoriesAprès = Bourse.objects.get(wallet=wallet, type='Bourse')
                assert categoriesAprès.amount < categoriesAvant.amount
                assert asset.number == assetAAPL.number-int(sell[data]['number_sold'])
            amount = 0
            assets = Asset.objects.filter(wallet=wallet)
            for asset in assets : 
                amount+=asset.actual_price*asset.number
        #Delete
        sell = Sells.objects.get(ticker=buy["API_Know"]["ticker"],wallet=wallet)
        url = reverse('delete_sell', kwargs={'pk': sell.id})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = api_client.delete(url,format='json')
        assert response.status_code == 204
        assert Sells.objects.filter(ticker=buy["API_Know"]["ticker"],wallet=wallet).exists()==False

    # on rachète des actifs déjà existant
    def testPostNewBuy(self, api_client,Newbuy, BuyFixture, register_user,user_token, buy):
        user = register_user
        access_token = user_token['access']
        wallet = Wallet.objects.get(user=user)
        #data à vérifier ensuite 
        categoriesAvant = Bourse.objects.get(wallet=wallet)
        categoriesCryptoAvant =  Crypto.objects.get(wallet=wallet)
        

        url = reverse('buy_asset')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        
        list = ["API_Know","unKnow"]
        for data in list:
            response = api_client.post(url,Newbuy[data],format='json')

            if data == "unKnow" or data == "API_Know":
                assert response.status_code == 201

                #on vérifie que asset, categorie et wallet a été créer  
                wallet1 = Wallet.objects.get(user=user)
                assert Buy.objects.filter(ticker=Newbuy[data]["ticker"],wallet=wallet).exists()
                asset = Asset.objects.get(ticker=Newbuy[data]["ticker"],wallet=wallet)
                if data == "unKnow":
                    categoriesCryptoAprès = Crypto.objects.get(wallet=wallet, type='Crypto')
                    assert categoriesCryptoAprès.amount > categoriesCryptoAvant.amount
                    assert HistoricalPrice.objects.filter(asset=asset).exists()
                else :
                    categoriesAprès = Bourse.objects.get(wallet=wallet, type='Bourse')
                    assert categoriesAprès.amount > categoriesAvant.amount
                assert asset.number == int(Newbuy[data]["number_buy"])+ int(buy[data]["number_buy"])
                assert wallet1.amount > wallet.amount

    def testModifAsset(self, api_client, BuyFixture, modif, register_user,user_token, buy):
        user = register_user
        access_token = user_token['access']
        url = reverse('maj_asset')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = api_client.patch(url,modif,format='json')
        assert response.status_code == 200

    def testPostCash(self, api_client,register_user,user_token,NewCashDetail):
        user = register_user
        access_token = user_token['access']
        url = reverse('cash-list')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        list = ["LEP","PEA","CTO"]
        for accounttype in list:
            response = api_client.post(url, NewCashDetail[accounttype], format='json')
            assert response.status_code == 201
            wallet = Wallet.objects.get(user=user)
            cashDetail=CashDetail.objects.get(wallet=wallet,account=NewCashDetail[accounttype]["account"])
            assert NewCashDetail[accounttype]["bank"]== cashDetail.bank
            assert NewCashDetail[accounttype]["amount"]== cashDetail.amount

    def testModifCashDetail(self, api_client,register_user,user_token,ModifCashDetail,PostCash, NewCashDetail):
        user = register_user
        wallet = Wallet.objects.get(user=user)
        access_token = user_token['access']
        cashs = PostCash
        modif = "LEP"
        count = 0
        for cash in cashs:
            if count==1:
                modif = "PEA"
            if count == 2:
                modif = "CTO"
            cash = CashDetail.objects.get(wallet=wallet,account=cash['account'], bank=cash['bank'])
            url = reverse('cash-detail', kwargs={'pk': cash.id})
            api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
            response = api_client.patch(url, ModifCashDetail[modif], format='json')
            assert response.status_code == 200
            wallet = Wallet.objects.get(user=user)
            cashDetail=CashDetail.objects.get(wallet=wallet,account=cash.account)
            if modif == "LEP" or modif == "PEA":
                assert int(NewCashDetail[modif]["amount"])+int(ModifCashDetail[modif]["addremove"])== cashDetail.amount
                assert NewCashDetail[modif]["bank"] == cashDetail.bank
            else:
                assert ModifCashDetail[modif]["amount"]== cashDetail.amount
                assert NewCashDetail[modif]["bank"] != cashDetail.bank

            #Je ne peux pas tester cette partie car il y a un delai d'une semaine avant que les données ne se stocke dans HistoricalWallet
            #print(HistoricalWallet.objects.get(wallet=wallet))
            #assert HistoricalWallet.objects.filter(wallet=wallet, value=cash.amount).exists()
            #assert HistoricalCash.objects.filter(wallet=wallet, value=cash.amount).exists()

            #essayer de supprimer le fichier
            response = api_client.delete(url, format='json')
            assert response.status_code == 204
            count+=1

    #La modif et la création
    def testRealEstateDetail(self,api_client,NewRealEstate,ModifRealEstate, register_user,user_token):
        user = register_user
        wallet = Wallet.objects.get(user=user)
        access_token = user_token['access']
        list = ["Full_data","Less_data"]
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        for data in list :
            url = reverse('new_realEstate')
            response = api_client.post(url,NewRealEstate[data],format='json')
            print(response.data)
            assert response.status_code == 201
            realEstate = RealEstate.objects.get(wallet=wallet)
            assert  RealEstateDetail.objects.filter(realestate = realEstate).exists()
            immo = RealEstateDetail.objects.get(realestate = realEstate, adresse = NewRealEstate[data]["adresse"])
            assert immo.actual_value == NewRealEstate[data]["buy_price"]
            #Modif
            url = reverse('maj_realEstate', kwargs={'pk': immo.id})
            response = api_client.patch(url,ModifRealEstate[data],format='json')
            assert response.status_code == 200
            immo = RealEstateDetail.objects.get(adresse = ModifRealEstate[data]["adresse"])
            assert ModifRealEstate[data]["actual_value"]==immo.actual_value

    


#Création Buy et Création Sell (Not API_know)
#Rachat d'un asset
#delete buy et sell  (API_know)
#Modif Asset (Not API_know)
#Creation RealEstateDetail(Vérifie que actual value se mette à jour en même temps)
#Modification RealEstateDetail
#Creation CashDetail
#Modification CashDetail (dont le amount via une soustraction ou un augmentation si buy ou sel) => véirfier le stockage de HistoricalPrice et HistoricalWaller
#Modification CashDetail (dont le amount ou il faut directement modifier le montant ) => véirfier le stockage de HistoricalPrice et HistoricalWaller
#Supprimer le compte CashDetail