#pytest --disable-warnings

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
import yfinance as yf
import math
from datetime import datetime
from django.utils.dateparse import parse_datetime

@pytest.fixture
def api_client():
    return APIClient()

# Create your tests here.
@pytest.mark.django_db
class TestAssetAPI:
    def test_create_assets(self, api_client):
        error = 0
        url = reverse('asset-list')
        tickers = ['AAPL','slv','BTC-USD','AAPL','TTE','DJIA']
        apple = 0
        for ticker in tickers: 
            payload = {'ticker':ticker}
            response = api_client.post(url,payload, format='json')
            if ticker == 'AAPL':
                apple +=1
            if apple == 2 and ticker == 'AAPL':
                assert response.status_code == 200
            else : 
                print(ticker)
                assert response.status_code == 201
            #on vérifie que tous les models ont été crées
            assert len(Asset.objects.filter(ticker = ticker.upper())) ==1
            asset = Asset.objects.get(ticker = ticker.upper())
            assert OldValue.objects.filter(asset = asset).exists()
            assert OneYearValue.objects.filter(asset = asset).exists()
            # on vérifie la validité des données dans Asset
            if ticker == 'BTC-USD':
                assert asset.category == 'Crypto'
            else : 
                assert asset.category == 'Bourse'
            data = yf.Ticker(ticker)
            info = data.info
            assert asset.company == info.get('shortName', None)
            assert asset.ticker == info.get('symbol')
            assert asset.isin_code == info.get('isin', None)
            assert asset.currency == info.get('currency', None)
            assert asset.type == info.get('quoteType', None)
            assert asset.country == info.get('country', None)
            assert asset.sector == info.get('sector', None)
            assert asset.industry == info.get('industry', None)
            if info.get('marketCap', None ) == None:
                assert asset.market_cap == None
            else : 
                tolerance = 0.01  # tolerance car on a certaine fois un float et d'autre fois un int 
                assert math.isclose(asset.market_cap, info.get('marketCap', None), rel_tol=tolerance)
            assert asset.beta == info.get('beta', None)
            history = data.history(period="1d")
            if history['Close'].iloc[-1] != None:
                assert asset.last_value == history['Close'].iloc[-1]
                assert asset.date_value == history.index[-1]

            # on vérifie les données de OneYearValue
            data = yf.download(ticker, group_by='column',start=timezone.now()-timedelta(days=365),end=timezone.now(), interval='1wk')
            last_date = None
            for date, value in data['Close'].items():
                #on vérifier qu'une donnée est bien existante avec ces données, qu'il n'y en a qu'une 
                if len(OneYearValue.objects.filter(asset = asset, date = date, value = value))!=1:
                    error += 1
                else :
                    value = OneYearValue.objects.get(asset = asset, date = date, value = value)
                    if last_date != None :
                        #on vérifie que chaque données est bien espacée d'une semaine
                        if last_date.isocalendar()[1]+1 == 53 : 
                            last_date = 1
                        else : 
                            last_date = last_date.isocalendar()[1]+1
                        assert last_date == value.date.isocalendar()[1]
                    last_date = value.date

            # on vérifie les données de OldValue
            data = yf.download(ticker, group_by='column',start='2000-01-01',end=timezone.now()-timedelta(days=365), interval='3mo')
            last_date = None
            for date, value in data['Close'].items():
                #on vérifier qu'une donnée est bien existante avec ces données, qu'il n'y en a qu'une 
                if len(OldValue.objects.filter(asset = asset, date = date, value = value)) != 1 :
                    error += 1
                else : 
                    value = OldValue.objects.get(asset = asset, date = date, value = value)
                    if last_date != None :
                        #on vérifie que chaque données est bien espacée de 3 mois
                        expected_date = last_date.month + 3
                        if expected_date > 12 :
                            expected_date -= 12
                        assert date.month == expected_date
                    last_date = value.date
        #on s'assure que deux asset du même ticker n'ont pas été créer 
        assert error < 3 #ici on vérifie que les dates qui ont sauté ne sont pas supérieur à 3
        assert len(Asset.objects.filter(ticker = 'AAPL')) == 1
        assert len(Asset.objects.all()) == 5

    def test_maj_asset(self, api_client):
        error = 0
        #on créer l'asset
        url = reverse('asset-list')
        payload = {'ticker':'AAPL'}
        response = api_client.post(url,payload, format='json')
        assert response.status_code == 201
        # on fait une requete de maj pour voir si ca marche même quand ca ne met pas à jour
        asset = Asset.objects.get(ticker='AAPL')
        url = reverse('asset-detail', kwargs={'pk': asset.pk})
        response = api_client.get(url, format='json')
        assert response.status_code == 200
        response_date = parse_datetime(response.data['date_value'])
        # Comparer les deux valeurs datetime
        assert asset.date_value == response_date
        assert asset.last_value == response.data['last_value']
        #on change les informations comme si l'asset n'avait pas été mis à jour depuis 430 jours
        #asset
        data=yf.download('AAPL', group_by='column',start=timezone.now()-timedelta(days=430), end=timezone.now()-timedelta(days=430), interval='1d')
        asset.date_value = data.index[0]
        asset.last_value = data['Close'].iloc[0]
        asset.save()
        asset = Asset.objects.get(ticker='AAPL')
        assert asset.date_value < timezone.now()-timedelta(days=429)
        #OneYearValue
        data = yf.download('AAPL', group_by='column',start=timezone.now()-timedelta(days=795),end=timezone.now()-timedelta(days=430), interval='1wk')
        OneYearValue.objects.filter(asset=asset).delete()
        for date, value in data['Close'].items():
                OneYearValue.objects.create(
                    asset = asset,
                    date = date,
                    value = value
                )  
        yearvalue = OneYearValue.objects.filter(asset=asset).latest('date')

        assert yearvalue.date < timezone.now()-timedelta(days=430)
        #OldValue
        data = yf.download('AAPL', group_by='column',start='2000-01-01',end=timezone.now()-timedelta(days=796), interval='3mo')
        OldValue.objects.filter(asset=asset).delete()
        for date, value in data['Close'].items():
                    OldValue.objects.create(
                        asset = asset,
                        date = date,
                        value = value,
                    )
        oldvalue = OldValue.objects.filter(asset=asset).latest('date')
        assert oldvalue.date < timezone.now()-timedelta(days=796)

        #On remet à jour
        url = reverse('asset-detail', kwargs={'pk': asset.pk})
        response = api_client.get(url, format='json')

        #on verifie l'asset
        assert response.status_code == 200
        assert (timezone.now()-timedelta(days=3)).date() < parse_datetime(response.data['date_value']).date()
        data = yf.download('AAPL', group_by='column',period='1d', interval='1d')
        assert data['Close'].iloc[-1] == response.data['price_value']
        # on vérifie les données de OneYearValue
        data = yf.download('AAPL', group_by='column',start=timezone.now()-timedelta(days=365),end=timezone.now(), interval='1wk')
        last_date = None
        for date, value in data['Close'].items():
            #on vérifier qu'une donnée est bien existante avec ces données, qu'il n'y en a qu'une 
            if len(OneYearValue.objects.filter(asset = asset, date = date, value = value))!=1:
                error += 1
            else :
                value = OneYearValue.objects.get(asset = asset, date = date, value = value)
                if last_date != None :
                    #on vérifie que chaque données est bien espacée d'une semaine
                    if last_date.isocalendar()[1]+1 == 53 : 
                        last_date = 1
                    else : 
                        last_date = last_date.isocalendar()[1]+1
                    assert last_date == value.date.isocalendar()[1]
                last_date = value.date

        #On vérifie que OldValue est à jour
        data = yf.download('AAPL', group_by='column',start='2000-01-01',end=timezone.now()-timedelta(days=365), interval='3mo')
        last_date = None
        for date, value in data['Close'].items():
            #on vérifier qu'une donnée est bien existante avec ces données, qu'il n'y en a qu'une 
            if len(OldValue.objects.filter(asset = asset, date = date, value = value)) != 1 :
                error += 1
            else : 
                value = OldValue.objects.get(asset = asset, date = date, value = value)
                if last_date != None :
                    #on vérifie que chaque données est bien espacée de 3 mois
                    expected_date = last_date.month + 3
                    if expected_date > 12 :
                        expected_date -= 12
                    assert date.month == expected_date
                last_date = value.date




        '''
        Ticker qui ne seront pas pris en charge sur yahoo finance
        Ticker envoyé dans post alors que déjà créer
        faire deux maj d'asset en moins d'un jour
        '''