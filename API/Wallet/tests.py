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
            "ticker":"EGLD",
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
            "ticker":"EGLD",
        },
        "unKnow2":{
            "currency":"USD",
            "name":"EGLD1",
            "plateforme":"Xportal",
            "account":"",
            "actual_price":"100",
            "ticker":"EGLD",
            "category":"Crypto",
        },
        "unKnow3":{ 
            "actual_price":"150",
            "ticker":"EGLD",
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
            "ticker":"EGLD",
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
        },
        "Less_data":{
        "type":'Appartement',
        "adresse":"12 rue Jean Jaures, Paris",
        "buy_date":"2020-12-26",
        "buy_price":250000,
        "apport":10000,
        "resteApayer":170000,
        "duration":20,
        }
    }
@pytest.fixture
def ModifRealEstate():# Vérifie que actual value se mette à jour en même temps
    return {
        "Full_data":{
        "adresse":"12 rue Jean Jaures, Paris",
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
        "CT":{
            "bank":"CA",
            "account":"CTO",
            "amount":2000,
        }
    }
@pytest.fixture
def ModifCashDetail():
    return{
        "CSL_LEP":{
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
        wallet = Wallet.objects.filter(user=user)
        url = reverse('buy_asset')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        
        list = ["API_Know","unKnow"]
        for data in list:
            response = api_client.post(url,buy[data],format='json')
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
        url = reverse('cash-list')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        list = ["LEP","PEA","CT"]
        for accounttype in list:
            response = api_client.post(url, NewCashDetail[accounttype], format='json')
            assert response.status_code == 201

@pytest.fixture
def RealEstateDetailfixture(api_client,NewRealEstate,ModifRealEstate, register_user,user_token):
        user = register_user
        access_token = user_token['access']
        list = ["Full_data","Less_data"]
        url = reverse('maj_realEstate')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        for data in list :
            response = api_client.post(url,NewRealEstate[data],format='json')
            assert response.status_code == 201
            immo = RealEstateDetail.objects.get(NewRealEstate[data]["adresse"])
            assert immo.actual_value == NewRealEstate[data]["buy_price"]
            #Modif
            url = reverse('maj_realEstate', kwargs={'pk': immo.id})
            response = api_client.patch(url,ModifRealEstate[data],format='json')
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
                print(f"wallet1 = {wallet1.amount} / Crypto : {crypto.amount} / Bourse : {bourse.amount}")
                print(response.data)
                assert Buy.objects.filter(ticker=buy[data]["ticker"],wallet=wallet).exists()
                assert Asset.objects.filter(ticker=buy[data]["ticker"],wallet=wallet).exists()
                asset = Asset.objects.get(ticker=buy[data]["ticker"],wallet=wallet)
                print(asset)
                assert asset.number == float(buy[data]['number_buy'])
                assert wallet1.amount > wallet.amount
            else :
                assert response.status_code == 400
        #On vérifie que les sous catégories ont été créer
        assert Crypto.objects.filter(wallet=wallet).exists()
        assert Bourse.objects.filter(wallet=wallet).exists()
        wallet1 = Wallet.objects.get(user=user)
        #Delete
        buy = Buy.objects.filter(ticker=buy["API_Know"]["ticker"],wallet=wallet)
        url = reverse('delete_buy', kwargs={'pk': buy.id})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = api_client.delete(url,format='json')
        assert response.status_code == 204
        assert not Buy.objects.filter(ticker=buy["API_Know"]["ticker"],wallet=wallet).exists()
        wallet2 = Wallet.objects.get(user=user)
        assert wallet1 > wallet2
    '''
    #post puis delete 
    def testPostSell(api_client,sell,BuyFixture,register_user,user_token):
        #data à vérifier ensuite 
        categoriesAvant = Bourse.objects.filter(wallet=wallet, type='Bouse')
        categoriesCryptoAvant =  Crypto.objects.filter(wallet=wallet, type='Crypto')
        assetAAPL = Asset.objects.filter(ticker='AAPL',wallet=wallet)
        assetEGLD =  Asset.objects.filter(ticker='EGLD',wallet=wallet)
        
        user = register_user
        access_token = user_token['access']
        wallet = Wallet.objects.filter(user=user)
        url = reverse('sell_asset')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        
        list = ["API_Know","unKnow"]
        for data in list:
            response = api_client.post(url,sell[data],format='json')

            assert response.status_code == 201

            #on vérifie que asset, categorie et wallet a été créer  
            wallet1 = Wallet.objects.filter(user=user)
            assert Buy.objects.filter(ticker=sell[data]["ticker"],wallet=wallet).exists()
            asset = Asset.objects.filter(ticker=sell[data]["ticker"],wallet=wallet)
            if data == "unKnow":
                categoriesCryptoAprès = Crypto.objects.filter(wallet=wallet, type='Crypto')
                assert categoriesCryptoAprès.amount < categoriesCryptoAvant.amount
                assert asset.number == assetEGLD.number-sell[data]['number']
            else :
                categoriesAprès = Bourse.objects.filter(wallet=wallet, type='Bourse')
                assert categoriesAprès.amount < categoriesAvant.amount
                assert asset.number == assetAAPL.number-sell[data]['number']
            assert wallet1.amount < wallet.amount
        #Delete
        sell = Sells.objects.filter(ticker=buy["API_Know"]["ticker"],wallet=wallet)
        url = reverse('delete_sell', kwargs={'pk': sell.id})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = api_client.delete(url,format='json')
        assert response.status_code == 204
        assert Sells.objects.filter(ticker=buy["API_Know"]["ticker"],wallet=wallet).exist()==False
        

    # on rachète des actifs déjà existant
    def testPostNewBuy(api_client,Newbuy, BuyFixture, register_user,user_token, buy):
        #data à vérifier ensuite 
        categoriesAvant = Bourse.objects.filter(wallet=wallet, type='Bouse')
        categoriesCryptoAvant =  Crypto.objects.filter(wallet=wallet, type='Crypto')
        
        user = register_user
        access_token = user_token['access']
        wallet = Wallet.objects.filter(user=user)
        url = reverse('buy_asset')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        
        list = ["API_Know","unKnow"]
        for data in list:
            response = api_client.post(url,Newbuy[data],format='json')

            if data == "unKnow" or data == "API_Know":
                assert response.status_code == 201

                #on vérifie que asset, categorie et wallet a été créer  
                wallet1 = Wallet.objects.filter(user=user)
                assert Buy.objects.filter(ticker=Newbuy[data]["ticker"],wallet=wallet).exists()
                asset = Asset.objects.filter(ticker=Newbuy[data]["ticker"],wallet=wallet)
                if data == "unKnow":
                    categoriesCryptoAprès = Crypto.objects.filter(wallet=wallet, type='Crypto')
                    assert categoriesCryptoAprès.amount > categoriesCryptoAvant.amount
                else :
                    categoriesAprès = Bourse.objects.filter(wallet=wallet, type='Bourse')
                    assert categoriesAprès.amount > categoriesAvant.amount

                assert asset.number == Newbuy[data]['number']+ buy[data]['number']
                assert wallet1.amount > wallet.amount

    # on rachète des actifs déjà existant
    def testPostNewBuy(api_client,Newbuy, BuyFixture, register_user,user_token, buy):
        #data à vérifier ensuite 
        categoriesAvant = Bourse.objects.filter(wallet=wallet, type='Bouse')
        categoriesCryptoAvant =  Crypto.objects.filter(wallet=wallet, type='Crypto')
        
        user = register_user
        access_token = user_token['access']
        wallet = Wallet.objects.filter(user=user)
        url = reverse('buy_asset')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        
        list = ["API_Know","unKnow"]
        for data in list:
            response = api_client.post(url,Newbuy[data],format='json')

            if data == "unKnow" or data == "API_Know":
                assert response.status_code == 201

                #on vérifie que asset, categorie et wallet a été créer  
                wallet1 = Wallet.objects.filter(user=user)
                assert Buy.objects.filter(ticker=Newbuy[data]["ticker"],wallet=wallet).exists()
                asset = Asset.objects.filter(ticker=Newbuy[data]["ticker"],wallet=wallet)
                if data == "unKnow":
                    categoriesCryptoAprès = Crypto.objects.filter(wallet=wallet, type='Crypto')
                    assert categoriesCryptoAprès.amount > categoriesCryptoAvant.amount
                else :
                    categoriesAprès = Bourse.objects.filter(wallet=wallet, type='Bourse')
                    assert categoriesAprès.amount > categoriesAvant.amount

                assert asset.number == Newbuy[data]['number']+ buy[data]['number']
                assert wallet1.amount > wallet.amount
    
    def testModifAsset(api_client, BuyFixture, modif, register_user,user_token, buy):
        user = register_user
        access_token = user_token['access']
        url = reverse('maj_asset')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = api_client.patch(url,modif,format='json')
        assert response.status_code == 200

    def testRealEstateDetail(api_client,NewRealEstate,ModifRealEstate, register_user,user_token):
        user = register_user
        access_token = user_token['access']
        list = ["Full_data","Less_data"]
        url = reverse('maj_realEstate')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        for data in list :
            response = api_client.post(url,NewRealEstate[data],format='json')
            assert response.status_code == 201
            immo = RealEstateDetail.objects.get(NewRealEstate[data]["adresse"])
            assert immo.actual_value == NewRealEstate[data]["buy_price"]
            #Modif
            url = reverse('maj_realEstate', kwargs={'pk': immo.id})
            response = api_client.patch(url,ModifRealEstate[data],format='json')
            assert response.status_code == 200
            immo = RealEstateDetail.objects.get(NewRealEstate[data]["adresse"])
            assert ModifRealEstate[data]["actual_value"]==immo.actual_value
    
    def testPostCash(api_client,register_user,user_token,NewCashDetail):
        user = register_user
        access_token = user_token['access']
        url = reverse('cash-list')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        list = ["LEP","PEA","CT"]
        for accounttype in list:
            response = api_client.post(url, NewCashDetail[accounttype], format='json')
            assert response.status_code == 201
            wallet = Wallet.objects.get(user=user)
            cashDetail=CashDetail.objects.filter(wallet=wallet,account=NewCashDetail[accounttype]["account"])
            assert NewCashDetail[accounttype]["bank"]== cashDetail.bank
            assert NewCashDetail[accounttype]["amount"]== cashDetail.amount

    def testModifCashDetail(api_client,register_user,user_token,ModifCashDetail,PostCash):
        user = register_user
        wallet = Wallet.objects.get(user=user)
        access_token = user_token['access']
        cashs = PostCash
        for cash in cashs:
            url = reverse('cash-detail', kwargs={'pk': cash.id})
            api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
            response = api_client.patch(url, ModifCashDetail[cash], format='json')
            assert response.status_code == 200
            wallet = Wallet.objects.get(user=user)
            cashDetail=CashDetail.objects.filter(wallet=wallet,account=NewCashDetail[cash]["account"])
            assert NewCashDetail[cash]["bank"]== cashDetail.bank
            if cash == "CSL_LEP" or cash == "PEA":
                assert NewCashDetail[cash]["amount"]== cashDetail.amount+cashs[cash]["amount"]
            else:
                assert NewCashDetail[cash]["amount"]== cashDetail.amount
            assert HistoricalWallet.objects.filter(cash=cash, value=cash.value).exists()
            assert HistoricalCash.objects.filter(wallet=wallet, value=cash.value).exists()
            # essayer de supprimer le fichier 
            response = api_client.delete(url, format='json')
            assert response.status_code == 204
'''


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