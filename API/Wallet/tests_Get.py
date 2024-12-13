import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from API.User.tests import register_user, account_fixture, user_token
from API.Wallet.tests import BuyFixture,PostCash,PostSell,RealEstateDetailfixture,NewRealEstate,ModifRealEstate,buy,sell,modif,Newbuy,NewRealEstate,ModifRealEstate,NewCashDetail,ModifCashDetail
from API.Wallet.models import Asset, Buy, Sells, Wallet, CryptoDetail, BourseDetail, CashDetail, RealEstate, RealEstateDetail, HistoricalPrice, HistoricalWallet, HistoricalCrypto, HistoricalBourse, HistoricalCash, HistoricalImmo, Bourse, Crypto, Cash
import django
django.setup()

User = get_user_model()

# je n'ai pas tester les historical price et historical wallet

@pytest.fixture
def api_client():
    return APIClient()

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
        assert response.data['amount'] == wallet.amount
        #test sur les autres catégories
        types = ['bourse','crypto','cash']
        for type in types:
            url = reverse('get_amount_of_categories', kwargs={'categorie':type})
            response = api_client.get(url, format='json')
            assert response.status_code == 200
            if type == 'bourse':
                categories = Bourse.objects.get(wallet=wallet)
            if type == 'crypto':
                categories = Crypto.objects.get(wallet=wallet)
            if type == 'cash':
                categories = Cash.objects.get(wallet=wallet)
            assert response.data['amount'] == categories.amount

    def testAllAssetList(self, api_client,BuyFixture,PostCash,PostSell,RealEstateDetailfixture,register_user,user_token):
        assetsResponse = 0
        immoSize = 0
        cashSize = 0
        user = register_user
        wallet = Wallet.objects.filter(user=user).first()
        access_token = user_token['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        types = ['bourse','crypto','cash','immo']
        for type in types:
            url = reverse("get_list_asset", kwargs={'categorie':type})
            response = api_client.get(url, format='json')
            assert response.status_code == 200
            if type == 'bourse' or type == 'crypto':
                assetsResponse+=len(response.data)
            elif type == 'cash':
                cashSize =len(response.data)
            else :
                immoSize=len(response.data)
        assets = Asset.objects.filter(wallet=wallet)
        cashs = CashDetail.objects.filter(wallet=wallet)
        immoG = RealEstate.objects.get(wallet=wallet)
        immos = RealEstateDetail.objects.filter(realestate=immoG)
        assert len(assets) == assetsResponse
        assert len(immos) == immoSize
        assert len(cashs) == cashSize

    def testActifPassif(self, api_client,BuyFixture,PostSell,RealEstateDetailfixture,register_user,user_token,NewRealEstate,ModifRealEstate):
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
                assert response.data['total'] > good_ValueActifAll-good_ValuePassif-10000 and response.data['total'] < good_ValueActifAll-good_ValuePassif+10000
            else:
                assert response.data['total'] > good_ValueActifImmo-good_ValuePassif-5000 and response.data['total'] < good_ValueActifImmo-good_ValuePassif+5000

    def testAnnualIncome(self, api_client,BuyFixture,PostCash,PostSell,RealEstateDetailfixture,register_user,user_token,NewRealEstate,ModifRealEstate):
        #On récupère les données immos de la fixture
        good_Income = ModifRealEstate["Less_data"]["loyer_annuel"]+NewRealEstate["Full_data"]["loyer_annuel"]
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
        assert response.data[0]['name']=="aple"
        #je ne vérifie pas que les valeurs retournées sont cohérante 
         
    def testGetOneAsset(self, api_client,BuyFixture,PostCash,PostSell,RealEstateDetailfixture,register_user,user_token,NewRealEstate,ModifRealEstate):
        user = register_user
        wallet = Wallet.objects.filter(user=user).first()
        asset = Asset.objects.filter(wallet=wallet).first()
        access_token = user_token['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        if asset.category == 'Bourse':
            cat = 'bourse'
        else :
            cat = 'crypto'
        url = reverse("get_info_asset", kwargs={'categorie':cat ,'pk':asset.pk})
        response = api_client.get(url, format='json')
        assert response.status_code == 200
        assert asset.name==response.data['asset']['name']
        assert asset.number==response.data['asset']['number']
        assert asset.company==response.data['asset']['company']
        assert asset.ticker==response.data['asset']['ticker']
        assert asset.ticker==response.data['asset']['ticker']
 
    def testHistoriqueAchat(self, api_client,BuyFixture,PostCash,PostSell,RealEstateDetailfixture,register_user,user_token,NewRealEstate,ModifRealEstate):
        user = register_user
        wallet = Wallet.objects.filter(user=user).first()
        asset = Asset.objects.filter(wallet=wallet).first()
        access_token = user_token['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        url = reverse("get_historique_transaction", kwargs={'categorie':'bourse'})
        response = api_client.get(url,format='json')
        assert response.status_code == 200
        print(response.data)
        assert len(response.data)==1 #il y a un premier achats de Apple 
        assert response.data[0]["achats"][0]["date_buy"] == "2024-07-12"

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
        assert len(datas) == historiqueAll.count()
        #assert len(datas)==7 # C'est le nom de nouvelle données que j'ai envoyé dans tests


        

#Obtenir le montant des categories
#Obtenir la list des assets
#Obtenir la liste Actif/Passif
#Obtenir les revenus annualisés de l'immo
#Obtenir les données propre à un Asset
#Obtenir le Momentum
#Obtenir l'historique des transactions
#Obtenir les historiques de All, Crypto, Bourse, Cash ou Immo,
