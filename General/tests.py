#pytest --disable-warnings
#pytest --disable-warnings tests.py::TestCurrencyAPI::test_currency

import pandas as pd
import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from General.models import Asset, Currency, OldValue, OneYearValue
import yfinance as yf
import math
from datetime import datetime
from django.utils.dateparse import parse_datetime
from unittest.mock import patch
from django.utils.dateparse import parse_datetime
import pytz
import django
django.setup()
'''
Il me manque les tests suivants mais je pense qu'ils ne sont pas nécessaires : 
    Asset : 
        - vérifier le retour de données de vue de détail (car pour l'instant je vérifie que les données dans la db direct suite à la maj)
        - vérifier les données retournées dans la vue de liste 
        - vérifier le retour si une requete get detail est mauvaise
        
'''
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
                print(response.data)
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
                date = history.index[-1]
                if isinstance(history.index[-1], pd.Timestamp):
                    date = date.to_pydatetime() 
                assert asset.date_value == date.replace(tzinfo=None).date() 

            # on vérifie les données de OneYearValue
            data = yf.download(ticker, group_by='column',start=timezone.now()-timedelta(days=365),end=timezone.now(), interval='1wk')
            last_date = None
            data.columns = ['_'.join(col).strip() for col in data.columns.values]
            for date, value in data[f'Close_{ticker.upper()}'].items():
                if isinstance(date, pd.Timestamp):
                    date = date.to_pydatetime()  # Convertir en datetime
                    if isinstance(date, datetime):
                        date = date.replace(tzinfo=None) 
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
            data.columns = ['_'.join(col).strip() for col in data.columns.values]
            for date, value in data[f'Close_{ticker.upper()}'].items():
                if isinstance(date, pd.Timestamp):
                    date = date.to_pydatetime()  # Convertir en datetime
                    if isinstance(date, datetime):
                        date = date.replace(tzinfo=None)
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
        now = timezone.now().date()
        tickers = ['AAPL','slv','jdenjnjed']
        for ticker in tickers :
            for date in dates :
                date = datetime.strptime(date, '%Y-%m-%d')
                if ticker != 'jdenjnjed':
                    # dates à initialiser
                    asset = yf.download(ticker, group_by='column',start=date-timedelta(days=1),end=date, interval='1d')
                    asset.columns = ['_'.join(col).strip() for col in asset.columns.values]
                    asset_price = asset[f'Close_{ticker.upper()}'].iloc[-1]
                    OneYearValue_data = yf.download(ticker, group_by='column',start=date-timedelta(days=365),end=date, interval='1wk') 
                    OneYearValue_data.columns = ['_'.join(col).strip() for col in OneYearValue_data.columns.values]
                    OldValue_data = yf.download(ticker, group_by='column',start='2000-01-01',end=date-timedelta(days=365), interval='3mo')
                    OldValue_data.columns = ['_'.join(col).strip() for col in OldValue_data.columns.values]
                    #date d'aujourd'hui
                    date_today = timezone.now()
                    data = yf.Ticker(ticker)
                    history = data.history(period="1d")
                    if history['Close'].iloc[-1] != None:
                        asset_today = history['Close'].iloc[-1]
                        last_date_today = history.index[-1].date()
                    else : 
                        asset_today = 0
                        last_date_today = timezone.now().date()
                    OneYearValue_today= yf.download(ticker, group_by='column',start=timezone.now()-timedelta(days=365),end=timezone.now(), interval='1wk') 
                    OneYearValue_today.columns = ['_'.join(col).strip() for col in OneYearValue_today.columns.values]
                    OldValue_today = yf.download(ticker, group_by='column',start='2000-01-01',end=timezone.now()-timedelta(days=365), interval='3mo')
                    OldValue_today.columns = ['_'.join(col).strip() for col in OldValue_today.columns.values]
            #On initialise les données à l'ancienne date 
            with patch('django.utils.timezone.now') as mock_now:
                mock_now.return_value = date.replace(tzinfo=utc)
                assert timezone.now().date() == date.date()
                assert timezone.now().date() != now
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
                    print(response.data)
                    assert response.status_code == 201
                # on fait une requete de maj pour voir si ca marche même quand ca ne met pas à jour
                asset_1 = Asset.objects.get(ticker=ticker.upper())
                url = reverse('asset-detail', kwargs={'pk': asset_1.pk})
                response = api_client.get(url, format='json')
                assert response.status_code == 200
                response_date = parse_datetime(response.data['date_value'])
                # on verifie qu'il n'y a pas de changement entre la création et la maj 
                assert asset_1.date_value == response_date.date()
                assert asset_1.last_value == response.data['last_value']
                #on fait les modifs de asset
                asset_1.last_value = asset_price
                asset_1.date_value = date.date()
                asset_1.save()
                #on vérifie que les données ont bien était initialisé à une date plus anciennes
                asset_1 = Asset.objects.get(ticker=ticker.upper())
                assert date.replace(tzinfo=None).date() == asset_1.date_value
                assert asset_price == asset_1.last_value
                #On supprime les anncienne données et on initialise les données de OneYearValue à la date ancienne
                OneYearValue.objects.filter(asset=asset_1).delete()
                for date, value in OneYearValue_data[f'Close_{ticker.upper()}'].items():
                    OneYearValue.objects.create(
                    asset = asset_1,
                    date = date.date(),
                    value = value
                )  
                yearvalue = OneYearValue.objects.filter(asset=asset_1).latest('date')
                assert yearvalue.date < timezone.now().date()
                #On supprime les anncienne données et on initialise les données de OldValue à la date ancienne
                OldValue.objects.filter(asset=asset_1).delete()
                for date, value in OldValue_data[f'Close_{ticker.upper()}'].items():
                    OldValue.objects.create(
                    asset = asset_1,
                    date = date.date(),
                    value = value
                )  
                oldvalue = OldValue.objects.filter(asset=asset_1).latest('date')
                assert oldvalue.date < timezone.now().date()-timedelta(days=365)
            # On vérifie qu'on est à la date d'ajd
            assert timezone.now().date() == now
            #On remet à jour
            url = reverse('asset-detail', kwargs={'pk': asset_1.pk})
            response = api_client.get(url, format='json')
            asset_2 = Asset.objects.get(ticker=ticker.upper())
            #on verifie l'asset mis à jour 
            assert response.status_code == 200
            assert asset_1.date_value < asset_2.date_value
            response_date = response.data['date_value']
            response_date_obj = datetime.strptime(response_date, "%Y-%m-%d").date()
            if last_date_today is not None:
                last_date_today_naive = last_date_today
            #else:
                #last_date_today_naive = last_date_today

            # Comparer les deux dates maintenant en UTC
            assert response_date_obj == last_date_today_naive
            # on vérifie les données de OneYearValue 
            for date, value in OneYearValue_today[f'Close_{ticker.upper()}'].items():
                #on vérifier qu'une donnée est bien existante avec ces données, qu'il n'y en a qu'une 
                if len(OneYearValue.objects.filter(asset = asset_2, date = date, value = value))!=1:
                    error += 1
                yearvalue = OneYearValue.objects.filter(asset=asset_1).earliest('date')
                assert yearvalue.date > timezone.now().date()-timedelta(days=365)
            #On vérifie que OldValue est à jour
            for date, value in OldValue_today[f'Close_{ticker.upper()}'].items():
                #on vérifier qu'une donnée est bien existante avec ces données, qu'il n'y en a qu'une 
                if len(OldValue.objects.filter(asset = asset_2, date = date, value = value)) != 1 :
                    error += 1
                oldvalue = OldValue.objects.filter(asset=asset_1).latest('date')
                assert oldvalue.date < timezone.now().date()-timedelta(days=365)
        assert error < 3



    def test_asset_action(self, api_client):
        url = reverse('asset-list')
        payload = {'ticker':'AAPL'}
        response = api_client.post(url,payload, format='json')
        print(response.data)
        assert response.status_code == 201
        asset = Asset.objects.get(ticker = 'AAPL')
        # modifier
        url = reverse('asset-detail', kwargs={'pk': asset.pk})
        payload = {'ticker':'MSFT'}
        response = api_client.patch(url,payload, format='json')
        assert response.status_code == 405
        exist = Asset.objects.filter(ticker = 'MSFT').exists()
        assert exist == False
        response = api_client.put(url,payload, format='json')
        assert response.status_code == 405
        exist = Asset.objects.filter(ticker = 'MSFT').exists()
        assert exist == False
        # delete
        response = api_client.delete(url, format='json')
        assert response.status_code == 405
        exist = Asset.objects.filter(ticker = 'AAPL').exists()
        assert exist == True
    


@pytest.mark.django_db
class TestSearchAPI:
    def test_search_asset(self,api_client):
        #version plus longue
        '''keywords = [
            'Google-Tesla','Amazon','S&P 500','FTSE 100','Nikkei','Argent','Platine','Vanguard','SPDR','iShares',
            'Bitcoin','Ripple','Technologie','Automobile','Energie','Schatz','Tokyo',
            'Paris','Tesla Motors','Goldman Sachs']
        '''
        keywords = [
            'Google-Tesla','Amazon','S&P 500','FTSE 100','Nikkei']
        for keyword in keywords :
                url = reverse('search_other_assets', args=[keyword])
                response = api_client.get(url, format='json')
                print(f'{keyword}:{response.status_code}')
                assert response.status_code == 200

@pytest.mark.django_db
class TestCurrencyAPI:
    def test_currency(self,api_client):
        error = 0
        url = reverse('asset-list')
        payload = {'ticker':'BTC-USD'}
        response = api_client.post(url,payload, format='json')
        print(response.data)
        assert response.status_code == 201
        #dates à initialiser 
        date = datetime.strptime('2021-01-01', '%Y-%m-%d')
        data = yf.download('BTC-USD', group_by='column',start=date-timedelta(days=1),end=date, interval='1d')
        data.columns = ['_'.join(col).strip() for col in data.columns.values]
        asset_price = data['Close_BTC-USD'].iloc[-1]
        asset_date = data.index[-1]
        OneYearValue_data = yf.download('BTC-USD', group_by='column',start=date-timedelta(days=365),end=date, interval='1wk') 
        asset = Asset.objects.get(ticker = 'BTC-USD')
        asset.currency = 'EUR'
        asset.last_value = asset_price
        asset.date_value = asset_date
        asset.save()
        # On supprime les données au dessus de '2021-01-01'
        OneYearValue.objects.filter(asset=asset, date__gt = date).delete()
        OneYearValue_data.columns = ['_'.join(col).strip() for col in OneYearValue_data.columns.values]
        for date, value in OneYearValue_data[f'Close_BTC-USD'].items():
                    OneYearValue.objects.create(
                    asset = asset,
                    date = date,
                    value = value
                )  
        OldValue.objects.filter(asset=asset, date__gt = date-timedelta(days=365)).delete()
        #Puis on refait une requete de maj pour voir si les date se sont mise à jour cette fois ci en eur
        url = reverse('asset-detail', kwargs={'pk':asset.pk})
        response = api_client.get(url, format='json')
        print(response.data)
        assert response.status_code == 200
        #on vérifie que device a bien été généré : 
        device = Currency.objects.get(device = 'USD/EUR')
        rate = device.rate
        assert device.date.date() == timezone.now().date()
        #on recupère les données nouvellement générées
        OneYearValue_data = yf.download('BTC-USD', group_by='column',start=timezone.now()-timedelta(days=365),end=timezone.now(), interval='1wk') 
        OneYearValue_data.columns = ['_'.join(col).strip() for col in OneYearValue_data.columns.values]
        OldValue_data = yf.download('BTC-USD', group_by='column',start='2000-01-01',end=timezone.now()-timedelta(days=365), interval='3mo')
        OldValue_data.columns = ['_'.join(col).strip() for col in  OldValue_data.columns.values]
        data = yf.download('BTC-USD', group_by='column',start=timezone.now()-timedelta(days=1),end=timezone.now(), interval='1d')
        data.columns = ['_'.join(col).strip() for col in data.columns.values]
    # on vérifie que les données sont en usd
        #asset
        asset = Asset.objects.get(ticker = 'BTC-USD')
        assert asset.last_value == data['Close_BTC-USD'].iloc[-1]*rate
        #OneYearValue
        for date, value in OneYearValue_data['Close_BTC-USD'].items():
            if len(OneYearValue.objects.filter(asset = asset, date = date, value = value*rate))!=1:
                    error += 1
        #OldValue
        for date, value in OldValue_data['Close_BTC-USD'].items():
            if date > datetime.strptime('2021-01-01', '%Y-%m-%d'):
                if len(OldValue.objects.filter(asset = asset, date = date, value = value*rate)) != 1 :
                            error += 1
        assert error < 3





