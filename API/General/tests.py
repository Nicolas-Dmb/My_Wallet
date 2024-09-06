#pytest --disable-warnings

import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Asset, Currency, OldValue, OneYearValue
import yfinance as yf
import math
from datetime import datetime
from django.utils.dateparse import parse_datetime
from unittest.mock import patch
from django.utils.dateparse import parse_datetime
import pytz

@pytest.fixture
def api_client():
    return APIClient()

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
            # risque de int et de float sur marketcap donc on doit le vérifier comme ca :
            market_cap_info = info.get('marketCap')
            if market_cap_info is None or asset.market_cap is None :
                assert asset.market_cap == market_cap_info
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
        assert error < 5 #ici on vérifie que les dates qui ont sauté ne sont pas supérieur à 3
        assert len(Asset.objects.filter(ticker = 'AAPL')) == 1
        assert len(Asset.objects.all()) == 5

    def test_maj_asset(self, api_client):
        utc = pytz.UTC
        error = 0
        dates = ["2018-05-15","2020-01-01"]
        now = timezone.now()
        tickers = ['AAPL','slv','jdenjnjed']
        for ticker in tickers :
            for date in dates :
                date = datetime.strptime(date, '%Y-%m-%d')
                if ticker != 'jdenjnjed':
                    #dates à initialiser 
                    asset = yf.download(ticker, group_by='column',start=date-timedelta(days=1),end=date, interval='1d')
                    asset_price = asset['Close'].iloc[-1]
                    OneYearValue_data = yf.download(ticker, group_by='column',start=date-timedelta(days=365),end=date, interval='1wk') 
                    OldValue_data = yf.download(ticker, group_by='column',start='2000-01-01',end=date-timedelta(days=365), interval='3mo')
                    #date d'aujourd'hui
                    date_today = timezone.now()
                    data = yf.Ticker(ticker)
                    history = data.history(period="1d")
                    if history['Close'].iloc[-1] != None:
                        asset_today = history['Close'].iloc[-1]
                        last_date_today = history.index[-1]
                    else : 
                        asset_today = 0
                        last_date_today = timezone.now()
                    OneYearValue_today= yf.download(ticker, group_by='column',start=timezone.now()-timedelta(days=365),end=timezone.now(), interval='1wk') 
                    OldValue_today = yf.download(ticker, group_by='column',start='2000-01-01',end=timezone.now()-timedelta(days=365), interval='3mo')
            #On initialise les données à l'ancienne date 
            with patch('django.utils.timezone.now') as mock_now:
                mock_now.return_value = date.replace(tzinfo=utc)
                assert timezone.now().date() == date.date()
                assert timezone.now() != now
                error = 0
                #on créer l'asset
                url = reverse('asset-list')
                payload = {'ticker':ticker}
                response = api_client.post(url,payload, format='json')
                if ticker == 'jdenjnjed':
                    assert response.status_code == 400
                    assert response.data == {"error":"actif inaccessible"}
                    return
                else : 
                    assert response.status_code == 201
                # on fait une requete de maj pour voir si ca marche même quand ca ne met pas à jour
                asset_1 = Asset.objects.get(ticker=ticker.upper())
                url = reverse('asset-detail', kwargs={'pk': asset_1.pk})
                response = api_client.get(url, format='json')
                assert response.status_code == 200
                response_date = parse_datetime(response.data['date_value'])
                # on verifie qu'il n'y a pas de changement entre la création et la maj 
                assert asset_1.date_value.date() == response_date.date()
                assert asset_1.last_value == response.data['last_value']
                #on fait les modifs de asset
                asset_1.last_value = asset_price
                asset_1.date_value = date.date()
                asset_1.save()
                #on vérifie que les données ont bien était initialisé à une date plus anciennes
                asset_1 = Asset.objects.get(ticker=ticker.upper())
                assert date.replace(tzinfo=utc) == asset_1.date_value
                assert asset_price == asset_1.last_value
                #On supprime les anncienne données et on initialise les données de OneYearValue à la date ancienne
                OneYearValue.objects.filter(asset=asset_1).delete()
                for date, value in OneYearValue_data['Close'].items():
                    OneYearValue.objects.create(
                    asset = asset_1,
                    date = date,
                    value = value
                )  
                yearvalue = OneYearValue.objects.filter(asset=asset_1).latest('date')
                assert yearvalue.date < timezone.now()
                #On supprime les anncienne données et on initialise les données de OldValue à la date ancienne
                OldValue.objects.filter(asset=asset_1).delete()
                for date, value in OldValue_data['Close'].items():
                    OldValue.objects.create(
                    asset = asset_1,
                    date = date,
                    value = value
                )  
                oldvalue = OldValue.objects.filter(asset=asset_1).latest('date')
                assert oldvalue.date < timezone.now()-timedelta(days=365)
            # On vérifie qu'on est à la date d'ajd
            assert timezone.now().date() == now.date()
            #On remet à jour
            url = reverse('asset-detail', kwargs={'pk': asset_1.pk})
            response = api_client.get(url, format='json')
            asset_2 = Asset.objects.get(ticker=ticker.upper())
            #on verifie l'asset mis à jour 
            assert response.status_code == 200
            assert asset_1.date_value < asset_2.date_value
            response_date = response.data['date_value']
            assert date_today.date() == last_date_today.date()
            assert asset_today == response.data['last_value']
            # on vérifie les données de OneYearValue
            for date, value in OneYearValue_today['Close'].items():
                #on vérifier qu'une donnée est bien existante avec ces données, qu'il n'y en a qu'une 
                if len(OneYearValue.objects.filter(asset = asset_2, date = date, value = value))!=1:
                    error += 1
                yearvalue = OneYearValue.objects.filter(asset=asset_1).earliest('date')
                assert yearvalue.date > timezone.now()-timedelta(days=365)
            #On vérifie que OldValue est à jour
            for date, value in OldValue_today['Close'].items():
                #on vérifier qu'une donnée est bien existante avec ces données, qu'il n'y en a qu'une 
                if len(OldValue.objects.filter(asset = asset_2, date = date, value = value)) != 1 :
                    error += 1
                oldvalue = OldValue.objects.filter(asset=asset_1).latest('date')
                assert oldvalue.date < timezone.now()-timedelta(days=365)
        assert error < 3

    def test_delet_asset(self, api_client):
        url = reverse('asset-list')
        payload = {'ticker':'AAPL'}
        response = api_client.post(url,payload, format='json')
        #essayer de modifier ou de supprimer

@pytest.mark.django_db
class TestSearchAPI:
    def test_search_asset(self,api_client):
        keywords = [
            'Google-Tesla','Amazon','S&P 500','FTSE 100','Nikkei','Argent','Cuivre','Platine','Vanguard','SPDR','iShares',
            'Bitcoin','Ripple','Technologie','Santé','Énergie','Automobile','Energie','Schatz','Tokyo',
            'Paris','New York','Tesla Motors','Microsoft Azure','Goldman Sachs']
        for keyword in keywords :
                url = reverse('search_other_assets', args=[keyword])
                response = api_client.get(url, format='json')
                print(f'{keyword}:{response.status_code}')
                assert response.status_code == 200

'''
    @patch('django.utils.timezone.now')
    def test_with_frozen_time(self, api_client):
        # Figer la date au 1er janvier 2020
        utc = pytz.UTC
        error = 0
        now = timezone.now()
        tickers = ['AAPL','slv']
        for ticker in tickers :
            date_2018_05_15 = datetime.strptime("2018-05-15", '%Y-%m-%d')
            asset_2018_05_15 = yf.download(ticker, group_by='column',start=date_2018_05_15-timedelta(days=1),end='2018-05-15', interval='1d')
            asset_2018_05_15 = asset_2018_05_15['Close'].iloc[-1]
            OneYearValue_2018_05_15 = yf.download(ticker, group_by='column',start=date_2018_05_15-timedelta(days=365),end='2018-05-15', interval='1wk') 
            OldValue_2018_05_15 = yf.download(ticker, group_by='column',start='2000-01-01',end=date_2018_05_15-timedelta(days=365), interval='3mo')
            asset_1 = {}
            date_2020_01_01 = datetime.strptime('2020-01-01', '%Y-%m-%d')
            asset_2020_01_01 = yf.download(ticker, group_by='column',start=date_2020_01_01-timedelta(days=1),end='2020-01-01', interval='1d')
            asset_2020_01_01 = asset_2020_01_01['Close'].iloc[-1]
            OneYearValue_2020_01_01 = yf.download(ticker, group_by='column',start=date_2020_01_01-timedelta(days=365),end='2020-01-01', interval='1wk') 
            OldValue_2020_01_01 = yf.download(ticker, group_by='column',start='2000-01-01',end=date_2020_01_01-timedelta(days=365), interval='3mo')
            asset_2 = {}
            date_today = timezone.now()
            asset_today = yf.Ticker(ticker)
            asset_today= asset_today.history(period="1d")
            asset_today= asset_today['Close'].iloc[-1]
            OneYearValue_today= yf.download(ticker, group_by='column',start=timezone.now()-timedelta(days=365),end=timezone.now(), interval='1wk') 
            OldValue_today = yf.download(ticker, group_by='column',start='2000-01-01',end=timezone.now()-timedelta(days=365), interval='3mo')
            asset_3 = {}

            with patch('django.utils.timezone.now') as mock_now:
                mock_now.return_value = datetime(2018, 5, 15, tzinfo=utc)
                #with freeze_time(date_2018_05_15):
                date = date_2018_05_15
                assert timezone.now().date() == date.date()
                assert timezone.now() != now
                error = 0
                #on créer l'asset
                url = reverse('asset-list')
                payload = {'ticker':ticker}
                response = api_client.post(url,payload, format='json')
                assert response.status_code == 201
                # on fait une requete de maj pour voir si ca marche même quand ca ne met pas à jour
                asset_1 = Asset.objects.get(ticker=ticker)
                url = reverse('asset-detail', kwargs={'pk': asset_1.pk})
                response = api_client.get(url, format='json')
                assert response.status_code == 200
                response_date = parse_datetime(response.data['date_value'])
                # on verifie qu'il n'y a pas de changement et que les prix correspondent à 2018
                assert asset_1.date_value.date() == response_date.date()
                assert asset_1.last_value == response.data['last_value']
                assert date_2018_05_15.date() == response_date.date()
                assert asset_2018_05_15 == response.data['last_value']
                # on vérifie les données de OneYearValue
                last_date = None
                for date, value in OneYearValue_2018_05_15['Close'].items():
                    #on vérifier qu'une donnée est bien existante avec ces données, qu'il n'y en a qu'une 
                    if len(OneYearValue.objects.filter(asset = asset_1, date = date, value = value))!=1:
                        error += 1
                    else :
                        value = OneYearValue.objects.get(asset = asset_1, date = date, value = value)
                        if last_date != None :
                            #on vérifie que chaque données est bien espacée d'une semaine
                            if last_date.isocalendar()[1]+1 == 53 : 
                                last_date = 1
                            else : 
                                last_date = last_date.isocalendar()[1]+1
                            assert last_date == value.date.isocalendar()[1]
                        last_date = value.date
                #On vérifie que OldValue est à jour
                last_date = None
                for date, value in OldValue_2018_05_15 ['Close'].items():
                    #on vérifier qu'une donnée est bien existante avec ces données, qu'il n'y en a qu'une 
                    if len(OldValue.objects.filter(asset = asset_1, date = date, value = value)) != 1 :
                        error += 1
                    else : 
                        value = OldValue.objects.get(asset = asset_1, date = date, value = value)
                        if last_date != None :
                            #on vérifie que chaque données est bien espacée de 3 mois
                            expected_date = last_date.month + 3
                            if expected_date > 12 :
                                expected_date -= 12
                            assert date.month == expected_date
                        last_date = value.date

            with patch('django.utils.timezone.now') as mock_now:
                mock_now.return_value = datetime(2020, 1, 1, tzinfo=utc)
                #with freeze_time(date_2020_01_01):
                date = date_2020_01_01
                # on fait une requete de maj pour voir si ca marche même quand ca ne met pas à jour
                url = reverse('asset-detail', kwargs={'pk': asset_1.pk})
                response = api_client.get(url, format='json')
                assert response.status_code == 200
                asset_2 = Asset.objects.get(ticker=ticker)
                assert asset_1.date_value < asset_2.date_value
                response_date = response.data['date']
                assert date_2020_01_01.date() == response_date.date()
                assert asset_2020_01_01 == response.data['last_value']
                # on vérifie les données de OneYearValue
                last_date = None
                for date, value in OneYearValue_2020_01_01['Close'].items():
                    #on vérifier qu'une donnée est bien existante avec ces données, qu'il n'y en a qu'une 
                    if len(OneYearValue.objects.filter(asset = asset_2, date = date, value = value))!=1:
                        error += 1
                    else :
                        value = OneYearValue.objects.get(asset = asset_2, date = date, value = value)
                        if last_date != None :
                            #on vérifie que chaque données est bien espacée d'une semaine
                            if last_date.isocalendar()[1]+1 == 53 : 
                                last_date = 1
                            else : 
                                last_date = last_date.isocalendar()[1]+1
                            assert last_date == value.date.isocalendar()[1]
                        last_date = value.date

                #On vérifie que OldValue est à jour
                last_date = None
                for date, value in OldValue_2020_01_01['Close'].items():
                    #on vérifier qu'une donnée est bien existante avec ces données, qu'il n'y en a qu'une 
                    if len(OldValue.objects.filter(asset = asset_2, date = date, value = value)) != 1 :
                        error += 1
                    else : 
                        value = OldValue.objects.get(asset = asset_2, date = date, value = value)
                        if last_date != None :
                            #on vérifie que chaque données est bien espacée de 3 mois
                            expected_date = last_date.month + 3
                            if expected_date > 12 :
                                expected_date -= 12
                            assert date.month == expected_date
                        last_date = value.date
 
            # On vérifie qu'on est à la date d'ajd
            assert timezone.now().date() == now
            #On remet à jour
            url = reverse('asset-detail', kwargs={'pk': asset_2.pk})
            response = api_client.get(url, format='json')
            asset_3 = Asset.objects.get(ticker=ticker)
            #on verifie l'asset mis à jour 
            assert response.status_code == 200
            assert asset_2.date_value < asset_3.date_value
            response_date = response.data['date']
            assert date_today.date() == response_date.date()
            assert asset_today == response.data['last_value']
            # on vérifie les données de OneYearValue
            last_date = None
            for date, value in OneYearValue_today['Close'].items():
                #on vérifier qu'une donnée est bien existante avec ces données, qu'il n'y en a qu'une 
                if len(OneYearValue.objects.filter(asset = asset_3, date = date, value = value))!=1:
                    error += 1
                else :
                    value = OneYearValue.objects.get(asset = asset_3, date = date, value = value)
                    if last_date != None :
                        #on vérifie que chaque données est bien espacée d'une semaine
                        if last_date.isocalendar()[1]+1 == 53 : 
                            last_date = 1
                        else : 
                            last_date = last_date.isocalendar()[1]+1
                        assert last_date == value.date.isocalendar()[1]
                    last_date = value.date

                    #On vérifie que OldValue est à jour
                    last_date = None
                    for date, value in OldValue_today['Close'].items():
                        #on vérifier qu'une donnée est bien existante avec ces données, qu'il n'y en a qu'une 
                        if len(OldValue.objects.filter(asset = asset_3, date = date, value = value)) != 1 :
                            error += 1
                        else : 
                            value = OldValue.objects.get(asset = asset_3, date = date, value = value)
                            if last_date != None :
                                #on vérifie que chaque données est bien espacée de 3 mois
                                expected_date = last_date.month + 3
                                if expected_date > 12 :
                                    expected_date -= 12
                                assert date.month == expected_date
                            last_date = value.date
                    assert error < 5'''
'''
Ticker qui ne seront pas pris en charge sur yahoo finance
Ticker envoyé dans post alors que déjà créer
faire deux maj d'asset en moins d'un jour
'''