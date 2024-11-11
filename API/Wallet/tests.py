import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.test import TestCase
from .models import Setting
from rest_framework import status



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
        "unKnow":{
            "currency":"USD",
            "name":"EGLD",
            "plateforme":"MAYAR",
            "account":"",
            "number_buy":"10",
            "price_buy":"200",
            "date_buy":"2023-01-12",
            "ticker":"EGLD",
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
def modif(request):#Il faudra ajouter wallet
    data= {
        "API_Know1":{
            "currency":'EUR',
            "name":"apple",
            "plateforme":"Revolut",
            "account":"CT",
        },
        "unKnow1":{
            "currency":"USD",
            "name":"EGLD",
            "plateforme":"Xportal",
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
        "adresse":"120 rue Jean Jaures, Paris",
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
        },
        "Less_data":{
        "loyer_annuel":10000,
        "charges_annuel":5000,
        "taxe":2000,
        "emprunt_costs":20000,
        "resteApayer":170000,
        "rate":2.2,
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
        "LEP":{
            "bank":"Societe Générale",
            "addremove":2000,
        },
        "PEA":{
            "addremove":-1000,
        },
    }
#Création Buy et Création Sell (API_know)
#Création Buy et Création Sell (Not API_know)
#Rachat d'un asset
#Modif Buy et Sell (API_know)
#Modif Asset (Not API_know)
#Creation RealEstateDetail(Vérifie que actual value se mette à jour en même temps)
#Modification RealEstateDetail
#Creation CashDetail
#Modification CashDetail (dont le amount via une soustraction ou un augmentation si buy ou sel) => véirfier le stockage de HistoricalPrice et HistoricalWaller
#Modification CashDetail (dont le amount ou il faut directement modifier le montant ) => véirfier le stockage de HistoricalPrice et HistoricalWaller
#Supprimer le compte CashDetail
#Obtenir le montant des categories 
#Obtenir la list des assets
#Obtenir la liste Actif/Passif 
#Obtenir l'historique des transaction
#Obtenir les revenus annualisés de l'immo
#Obtenir le Momentum
#Obtenir les données propre à un Asset
#Obtenir les historiques de All, Crypto, Bourse, Cash ou Immo,
