import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
import django
django.setup()



@pytest.fixture
def buy():
    return {
        "crypto":{
            "category" : "Crypto",
            "type" : '',
            "company" : "Bitcoin",
            "country" : None,
            "sector" : None,
            "industry" : None,
            "ticker" : "BTC",
            "currency" : "EUR",
            "last_value" : 90000.0,
            "date_value" : "2025-07-12",
            "market_cap" : 1000000.0,
            "isin_code" :  93782398,
            "beta" : None,
        },
        "bourse":{
            "category" : "Bourse",
            "type" : '',
            "company" : "Apple",
            "country" : "USA",
            "sector" : "Technology",
            "industry" : "Technology",
            "ticker" : "AAPL",
            "currency" : "USD",
            "last_value" : 500.0,
            "date_value" : "2025-07-12",
            "market_cap" : 2000000.0,
            "isin_code" :  93782334,
            "beta" : None,
        },
        "Cash":{
            "wallet" = models.ForeignKey(Wallet, on_delete=models.CASCADE)
            "bank"= models.CharField(max_length=50)
            "account" = models.CharField(max_length=50,choices=AccountTypes.choices, default=AccountTypes.CC)
            "amount" = models.FloatField(default=0)
        },
    }



@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class SearchTest:
    def testCrypto(self,mocker):
       
