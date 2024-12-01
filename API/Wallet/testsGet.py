import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from .tests import BuyFixture,PostCash,PostSell,RealEstateDetailfixture,NewRealEstate,ModifRealEstate
from .models import Asset, Buy, Sells, Categories, Wallet, CryptoDetail, BourseDetail, CashDetail, RealEstate, RealEstateDetail, HistoricalPrice, HistoricalWallet, HistoricalCrypto, HistoricalBourse, HistoricalCash, HistoricalImmo
import django
django.setup()


@pytest.mark.django_db
class TestGet:

    def testAmountCategories(self, api_client,BuyFixture,PostSell,PostCash,RealEstateDetailfixture,register_user,user_token):
        user = register_user
        access_token = user_token['access']
        #test sur all
        url = reverse('get_amount_of_categories', kwargs={'categorie':'all'})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = api_client.get(url, format='json')
        assert response.status_code == 200
        wallet = Wallet.objects.filter(user=user).first()
        assert response.data.amount == wallet.amount
        #test sur les autres catégories
        types = ['bourse','crypto','cash']
        for type in types:
            url = reverse('get_amount_of_categories', kwargs={'categorie':type})
            response = api_client.get(url, format='json')
            assert response.status_code == 200
            categories = Categories.objects.filter(wallet=wallet, type=type).first()
            assert response.data.amount == categories.amount

    def testAllAssetList(self, api_client,BuyFixture,PostCash,PostSell,RealEstateDetailfixture,register_user,user_token):
        assetsResponse = []
        user = register_user
        wallet = Wallet.objects.filter(user=user).first()
        access_token = user_token['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        types = ['bourse','crypto','cash','immo']
        for type in types:
            url = reverse("get_list_asset", kwargs={'categorie':type})
            response = api_client.get(url, format='json')
            assert response.status_code == 200
            assetsResponse.append(response.data)
        assets = Asset.objects.filter(wallet=wallet)
        immos = RealEstate.objects.get(wallet=wallet)
        immos = RealEstateDetail.objects.filter(realestate=immos)
        for asset in assets:
            assert asset in assetsResponse
        for immo in immos :
            assert immo in assetsResponse

    def testActifPassif(self, api_client,BuyFixture,PostCash,PostSell,RealEstateDetailfixture,register_user,user_token,NewRealEstate,ModifRealEstate):
        #On récupère les données immos de la fixture
        good_ValuePassif = NewRealEstate["Less_data"]["resteApayer"]+NewRealEstate["Full_data"]["resteApayer"]
        good_ValueActifImmo = ModifRealEstate["Less_data"]["actual_value"]+ModifRealEstate["Full_data"]["actual_value"]
        #Données de base 
        user = register_user
        wallet = Wallet.objects.filter(user=user).first()
        access_token = user_token['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        #All actif 
        good_ValueActifAll=good_ValueActifImmo
        assets = Asset.objects.filter(wallet=wallet)
        for asset in assets:
            good_ValueActifAll+=asset.actual_price
        #Appel api
        types = ['all','immo']
        for type in types:
            url = reverse("get_actif_passif", kwargs={'categorie':type})
            response = api_client.get(url, format='json')
            assert response.status_code == 200
            if type == 'all':
                assert response.data['total'] == good_ValueActifAll-good_ValuePassif
            else:
                assert response.data['total'] == good_ValueActifImmo-good_ValuePassif

    def testAnnualIncome(self, api_client,BuyFixture,PostCash,PostSell,RealEstateDetailfixture,register_user,user_token,NewRealEstate,ModifRealEstate):
        #On récupère les données immos de la fixture
        good_Income = NewRealEstate["Less_data"]["loyer_annuel"]+NewRealEstate["Full_data"]["loyer_annuel"]
        #appel API
        user = register_user
        wallet = Wallet.objects.filter(user=user).first()
        access_token = user_token['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        url = reverse("get_revenu_annuel")
        response = api_client.get(url, format='json')
        assert response.status_code == 200
        response_income = 0
        datas = response.data
        for data in datas:
            response_income += data['loyer_annuel']
        assert good_Income == response_income

    def testMomemtum(self, api_client,BuyFixture,PostCash,PostSell,RealEstateDetailfixture,register_user,user_token,NewRealEstate,ModifRealEstate):
        user = register_user
        asset = Asset.objects.filter(ticker="AAPL").first()
        access_token = user_token['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        url = reverse("get_momentum", kwargs={'categorie':"bourse"})
        response = api_client.get(url, format='json')
        assert response.status_code == 200
        assert response.data[0]['ticker']=="AAPL"
        assert response.data[0]['name']=="apple"
        #je ne vérifie pas que les valeurs retournées sont cohérante 
    
    def testGetOneAsset(self, api_client,BuyFixture,PostCash,PostSell,RealEstateDetailfixture,register_user,user_token,NewRealEstate,ModifRealEstate):
        user = register_user
        wallet = Wallet.objects.filter(user=user).first()
        asset = Asset.objects.filter(wallet=wallet).first()
        access_token = user_token['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        url = reverse("get_info_asset", kwargs={'categorie':asset.category ,'pk':asset.pk})
        response = api_client.get(url, format='json')
        assert response.status_code == 200
        assert asset.name==response.data['name']
        assert asset.number==response.data['number']
        assert asset.company==response.data['company']
        assert asset.ticker==response.data['ticker']
        assert asset.ticker==response.data['ticker']

    def testHistoriqueAchat(self, api_client,BuyFixture,PostCash,PostSell,RealEstateDetailfixture,register_user,user_token,NewRealEstate,ModifRealEstate):
        user = register_user
        wallet = Wallet.objects.filter(user=user).first()
        asset = Asset.objects.filter(wallet=wallet).first()
        access_token = user_token['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        url = reverse("get_historique_transaction", kwargs={'categorie':'bourse'})
        response = api_client.get(url,format='json')
        assert response.status_code == 200
        assert len(response.data)==2 #il y a deux achats de Apple 
        assert response.data[0]["date_buy"] == "2024-07-12"
        assert response.data[0]["date_buy"] == "2024-12-12"

    def testHistoriqueAmount(self, api_client,BuyFixture,PostCash,PostSell,RealEstateDetailfixture,register_user,user_token,NewRealEstate,ModifRealEstate):
        user = register_user
        wallet = Wallet.objects.filter(user=user).first()
        historiqueAll = HistoricalWallet.objects.filter(wallet=wallet)
        access_token = user_token['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        url = reverse("Get_perf_categories", kwargs={'categorie':"all"})
        response = api_client.get(url,format='json')
        assert response.status_code==200
        datas = response.data
        for data in datas:
            assert data in historiqueAll
            assert len(data) == len(historiqueAll)
            assert len(data)==7 # C'est le nom de nouvelle données que j'ai envoyé dans tests


        

#Obtenir le montant des categories
#Obtenir la list des assets
#Obtenir la liste Actif/Passif
#Obtenir les revenus annualisés de l'immo
#Obtenir les données propre à un Asset
#Obtenir le Momentum
#Obtenir l'historique des transactions
#Obtenir les historiques de All, Crypto, Bourse, Cash ou Immo,
