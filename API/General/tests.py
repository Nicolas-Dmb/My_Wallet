import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from datetime import timedelta
from django.test import TestCase
from .models import Asset, Currency, OldValue, OneYearValue
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
import os

@pytest.fixture
def api_client():
    return APIClient()
# Create your tests here.
@pytest.mark.django_db
class TestAssetAPI:
    def test_create_assets(self, api_client):
        url = reverse('asset-list')
        tickers = ['AAPL','SLV','BTC-USD']
        for ticker in tickers: 
            payload = {'ticker':ticker}
            response = api_client.post(url,payload, format='json')
            assert response.status_code == 201
            print(response.content)
            assert Asset.objects.filter(ticker = ticker).exists()
            asset = Asset.objects.get(ticker = ticker)
            assert OldValue.objects.filter(asset = asset).exists()
            assert OneYearValue.objects.filter(asset = asset).exists()




        '''
        Ticker qui ne seront pas pris en charge sur yahoo finance
        Ticker envoyé dans post alors que déjà créer
        faire deux maj d'asset en moins d'un jour
        '''