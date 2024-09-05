from django.db import models
from django.db import transaction
from django.conf import settings
from User.models import Setting
import requests
import yfinance as yf
from django.utils import timezone
from datetime import timedelta

'''
Tester : 
Si lent alors créer des taches asynchrones
    Asset : 
        - Category : tester la mise en place
        - Company : essayer d'obtenir le nom si j'ai que le ticker 
        - Ticker : essayer d'obtenir le ticker si j'ai que le nom 
        - currency : savoir si c'est en euro ou en dollar
        - last-value : mettre à jour la valeur de l'actif
        - date-value : mettre à jour la date de maj de la valeur 
        
        - maj asset : 
            - vérifier avec des données non encore saisie, d
            - des données déjà saisie
            - sur plusieurs assets et type d'assets
        - create asset : 
            - vérifier avec des données non encore saisie, d
            - des données déjà saisie
            - sur plusieurs assets

    OneYearValue : 
        - value : obtenir l'historique sur un an pour chaque week
        - create OneYearValue : 
            - vérifier avec des données non encore saisie, d
            - des données déjà saisie
            - sur plusieurs assets
    
    OldValue : 
        - value : obtenir l'historique sur les années antérieurs
        - create OldValue : 
            - vérifier avec des données non encore saisie, d
            - des données déjà saisie
            - sur plusieurs assets

    Currency : 
        - vérifier :- que les valeurs se mettent bien à jour d'un côté comme de l'autre
                    - qu'il n'y qu'une seule instance par paire de device        
'''
#Asset permet d'enregistrer uniquement les données extraites de yfinance et qui seront partagées par plusieurs comptes
class Asset(models.Model):
    class Categorys(models.TextChoices): 
        Crypto = 'Crypto', 
        Immo = 'Immo', 
        Bourse = 'Bourse', 
        Autre = 'Autre', 
    
    class CurrencyList(models.TextChoices): 
        Euro = 'Euro', 
        Dollar = 'Dollar',
    
    category = models.CharField(max_length=10, choices=Categorys.choices, null=True, blank=True)
    type = models.CharField(max_length=10, null=True, blank=True)
    company = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    sector = models.CharField(max_length=100, null=True, blank=True)
    industry = models.CharField(max_length=100, null=True, blank=True)
    ticker = models.CharField(max_length=10, unique=True)
    currency = models.CharField(max_length=10, default=CurrencyList.Euro, choices=CurrencyList.choices, blank=False)
    last_value = models.FloatField()
    date_value = models.DateTimeField()
    market_cap = models.FloatField(null=True, blank=True)
    isin_code =  models.IntegerField(null=True, blank=True)
    #trailing_return = models.FloatField(null=True, blank=True)
    #fee = models.FloatField(null=True, blank=True)
    #total_assets = models.FloatField(null=True, blank=True)  # Total des actifs en milliards ou millions
    #sector_weightings = models.JSONField(null=True, blank=True)  # Répartition sectorielle, stockée en tant que JSON
    #holding_percentages = models.JSONField(null=True, blank=True)  # Pourcentages de détention, stockée en tant que JSON
    #top_holdings = models.JSONField(null=True, blank=True)  # Top 10 des avoirs, stockés en tant que JSON
    beta = models.FloatField(null=True, blank=True)  # Beta du fonds
    
    #ici on fait une requête à l'API pour mettre à jour la valeur de l'actif si plus de 1 jours sans maj
    @transaction.atomic
    def maj_asset(self):
        if self is None :
            return "asset doesn't exist"
        #si plus de 1 jour sans maj
        if self.date_value > timezone.now()-timedelta(days=1):
            return True
        try :
            #on récupère les dernières données 
            data = yf.download(self.ticker, group_by='column',period='1d', interval='1d')
            info = data.info
            # Vérifier si les données sont disponibles
            if info.get('shortName')==None:
                return "Asset not available in yfinance"
            #on vérifie la device retournée 
            currency = data.info.get('currency')
            rate = 1
            if currency != self.currency : 
                response = Currency.know_rate(currency, self.currency)
                if response : 
                    rate = Currency.objects.get(device = f"{currency}/{self.currency}").rate
            #on récupère la dernière donnée pour asset 
            self.last_value=data['Close'].iloc[-1] * rate
            self.date_value=data.index[-1]
            self.market_cap = data.info('marketcap', None)
            self.beta = data.info('beta', None)
            self.currency = data.info('currency',None)
            self.save()
            #On récupère toutes les données de data pour les ajouters à OneYearValue par semaine 
            historical = OneYearValue.objects.filter(asset = self).latest("date")
            data = yf.download(self.ticker, group_by='column',start=historical.date,end=timezone.now(), interval='1wk')
            for date, value in data['Close'].items():
                OneYearValue.objects.create(asset = self, date=date, value=value*rate)
            #On supprime les données de OneYearValue supérieur à un an 
            OneYearValue.objects.filter(asset=self, date__lt=timezone.now()-timedelta(days=365)).delete()
            #On vient rajouter à OldValue les trimestres des années non encore enregistrée 
            oldvalues = OldValue.objects.filter(asset = self).latest('date')
            data = yf.download(self.ticker, group_by='column',start=oldvalues.date,end=timezone.now()-timedelta(days=365), interval='3mo')
            for date, value in data['Close'].items():
                OldValue.objects.create(asset = self, date=date, value=value*rate)
            return True
        except Exception as e:
            return f"Erreur lors de la mise à jour de l'actif : {e}"
            
    @transaction.atomic
    def create_asset(self, ticker):
        asset_exist = Asset.objects.filter(ticker=ticker).exists()
        if asset_exist:
            return 'Asset already exist'
        
        try:
            data = yf.Ticker(ticker)
            info = data.info
            # Vérifier si les données sont disponibles
            if info.get('shortName')==None:
                return "Asset not available in yfinance"
            
            # Création de l'instance de l'Asset
            asset = Asset(
                category='Crypto' if info.get('quoteType') == 'CRYPTOCURRENCY' else 'Bourse',
                company=info.get('shortName', None),
                ticker=info.get('symbol'),
                isin_code = info.get('isin', None),
                currency=info.get('currency', None),
                type=info.get('quoteType', None),
                country=info.get('country', None),
                sector=info.get('sector', None),
                industry=info.get('industry', None),
                market_cap=info.get('marketCap', None),
                beta=info.get('beta', None),
            )

            # Gestion de l'historique
            history = data.history(period="1d")
            if history['Close'].iloc[-1] != None:
                asset.last_value = history['Close'].iloc[-1]
                asset.date_value = history.index[-1]

            # Sauvegarde de l'instance Asset
            asset.save()
            return True
        
        except Exception as e:
            return f"Erreur lors de la création de l'actif : {e}"



class OneYearValue(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    date = models.DateTimeField()
    value = models.FloatField()

    @transaction.atomic
    def create_OneYearValue(self, ticker):
        try : 
            try:
                asset = Asset.objects.get(ticker=ticker)
            except Asset.DoesNotExist:
                return "Erreur lors de la création de l'asset 1"
            except Asset.MultipleObjectsReturned:
                return "Deux assets correspondents 1"

            if OneYearValue.objects.filter(asset=asset).exists():
                return "Ces données existent déjà 1"
            data = yf.download(ticker, group_by='column',start=timezone.now()-timedelta(days=365),end=timezone.now(), interval='1wk')
            for date, value in data['Close'].items():
                OneYearValue.objects.create(
                    asset = asset,
                    date = date,
                    value = value
                )       
            return True
        except Exception as e : 
            # Log l'erreur pour des diagnostics ultérieurs
            return f"Erreur lors de la creation de OneYearValue: {e}"

class OldValue(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    date = models.DateTimeField()
    value = models.FloatField() #je stocke les valeurs tous les 3 mois
    
    @transaction.atomic
    def create_OldValue(self, ticker):
        try : 
            try:
                asset = Asset.objects.get(ticker=ticker)
            except Asset.DoesNotExist:
                return "Erreur lors de la création de l'asset 2"
            except Asset.MultipleObjectsReturned:
                return "Deux assets correspondents 2"
            if OldValue.objects.filter(asset = asset).exists(): 
                return "Ces données existent déjà 2"
            oneyearvalue = OneYearValue.objects.filter(asset = asset).earliest("date")
            data = yf.download(ticker, group_by='column',start='2000-01-01',end=oneyearvalue.date, interval='3mo')
            for date, value in data['Close'].items():
                if date != oneyearvalue.date: 
                    OldValue.objects.create(
                        asset = asset,
                        date = date,
                        value = value,
                    )
            return True
        except Exception as e : 
            return f"Erreur lors de la creation de OldValue: {e}"

class Currency(models.Model):
    rate = models.DecimalField(max_digits=10, decimal_places=6)
    date = models.DateTimeField(auto_now_add=True)
    device = models.CharField(
        max_length=10, 
        choices=[
            ('USD/EUR', 'USD/EUR'),
            ('EUR/USD', 'EUR/USD'),
            ('GBP/EUR', 'GBP/EUR'),
            ('EUR/GBP', 'EUR/GBP'),
            ('JPY/EUR', 'JPY/EUR'),
            ('EUR/JPY', 'EUR/JPY'),
        ],
        unique=True
    )

    @transaction.atomic
    def know_rate(self, base='EUR', symbols='USD'):
        device_pair = f"{base}/{symbols}"
        recent_currency = Currency.objects.filter(device=device_pair).first()
        if recent_currency and recent_currency.date > timezone.now() - timedelta(days=1) :
            return True
        
        api_url = 'http://data.fixer.io/api/latest'
        params = {
            'access_key': settings.FIXER_KEY,
            'base': base,
            'symbols': symbols
        }
        try:
            #requete
            response = requests.get(api_url, params=params)
            response.raise_for_status()  # Vérifie les erreurs HTTP
            response_data = response.json()
            
            #traitement de la réponse
            if response_data.get('success'):
                if recent_currency :
                    recent_currency.rate = response_data['rates'].get(symbols)
                    recent_currency.device = f"{base}/{symbols}"
                    recent_currency.save()
                else :
                   Currency.objects.create(
                        rate=response_data['rates'].get(symbols),
                        device=device_pair
                    )
                return True
            else :  
                return False
        except requests.RequestException as e:
            return False