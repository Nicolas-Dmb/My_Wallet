from django.db import models
from django.conf import settings
from django.db import transaction
from django.utils import timezone

'''
test : 
    - si l'user ne saisie pas toutes les valeurs demandées'''

class Wallet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField(default=timezone.now)

    '''@transaction.atomic
        def maj_amount(self):
            A chaque nouvelle date je cumule les valeur de crypto/bourse/Immo/Cash et autre de l'user puis je créer un nouveau model wallet'''

    def __str__(self):
        return self.user

class Crypto(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField(default=timezone.now)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount_btc = models.FloatField()
    amount_eth = models.FloatField()
    amount_nft = models.FloatField()
    amount_stablecoins = models.FloatField()
    amount_altcoins = models.FloatField()
    
    '''@transaction.atomic
        def maj_amount(self):
            Je viens mettre à jour ce pf dès qu'une nouvelle valeur vient s'y ajouter depuis la date à laquelle elle a été achetée on vient valoriser les valeurs par celle achetées
            S'il fait une requete get on vient mettre à jour la dernière valeur et si plus d'un mois sans maj on vient aussi faire une deuxième maj pour comble la différence entre les deux majs.

    '''
    def __str__(self):
        return self.user

class CryptoDetailt(models.Model):
    class CategoryList(models.TextChoices):
        BTC = 'BTC'
        ETH = 'ETH'
        Stablecoins = 'Stablecoins'
        Altcoins = 'Altcoins'
        NFT = 'NFT'

    class FrequencyList(models.TextChoices):
        Year = 'Year'
        Month = 'Month'
        Week = 'Week'
        Day = 'Day'
        Hour = 'Hour'
        Minute = 'Minute'

    class CurrencyList(models.TextChoices): 
        EUR = 'EUR', 
        USD = 'USD',
        GBP = 'GBP',
        JPY = 'JPY',
    
    actual_price = models.FloatField()
    currency = models.CharField(max_length=10, default=CurrencyList.EUR, choices=CurrencyList.choices, blank=False)
    #Foreignkey
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #action
    buy = models.BooleanField(default=True)
    category = models.CharField(max_length=10, choices=CategoryList.choices, blank=False)
    name = models.CharField()
    plateforme = models.CharField(blank=False)
    account = models.CharField(blank=True)
    number_buy = models.FloatField(blank=False)
    price_buy_sold = models.FloatField(blank=False)
    date_buy_sold = models.DateTimeField(default=timezone.now)
    #stacking 
    stacking = models.BooleanField(default=False)
    rate_rewards = models.FloatField(default=0)
    rewards = models.CharField() #quel crypto est donnée en rewards
    last_reward_cal = models.DateTimeField()
    frequency = models.CharField(max_length=10, choices=CategoryList.choices, blank=False)
    #API:
    api_know = models.BooleanField(default=True)
    type = models.CharField(max_length=50, null=True, blank=True)
    ticker = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f'{self.user}{self.name}'
    '''@transaction.atomic
        def maj_amount(self):
            On vient mettre à jour le prix actuelle si c'est un buy
    '''

    '''@transaction.atomic
        def maj_reward_cal(self):
            On vient mettre à jour les rewards si c'est un buy
    '''

class Bourse(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField(default=timezone.now)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount_action = models.FloatField()
    amount_etf = models.FloatField()
    amount_forex = models.FloatField()
    amount_obligation = models.FloatField()
    amount_matières_premières = models.FloatField()
    '''@transaction.atomic
        def maj_amount(self):
            Je viens mettre à jour ce pf dès qu'une nouvelle valeur vient s'y ajouter depuis la date à laquelle elle a été achetée on vient valoriser les valeurs par celle achetées
            S'il fait une requete get on vient mettre à jour la dernière valeur et si plus d'un mois sans maj on vient aussi faire une deuxième maj pour comble la différence entre les deux majs.

    '''
    '''@transaction.atomic
        def receive inf about api(self):
        - si certaine info ne sont pas donné par l'user comme catégorie etc alors je les récupère auprès de l'API.
    '''
class BourseDetail(models.Model):
    class FrequencyList(models.TextChoices):
        Annuelle = 'Annuelle'
        Semestrielle = 'Semestrielle'
        Trimestrielle = 'Trimestrielle'

    class CategoryList(models.TextChoices):
        Action = 'Action'
        ETF = 'ETF'
        Forex = 'Forex'
        Matières_Premières = 'Matières_Premières'

    class CurrencyList(models.TextChoices): 
        EUR = 'EUR',
        USD = 'USD',
        GBP = 'GBP',
        JPY = 'JPY',

    actual_price = models.FloatField()
    currency = models.CharField(max_length=10, default=CurrencyList.EUR, choices=CurrencyList.choices, blank=False)
    #Foreignkey
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #action envoyé par l'user
    buy = models.BooleanField(default=True)
    category = models.CharField(max_length=10, choices=CategoryList.choices, blank=False)
    name = models.CharField()
    plateforme = models.CharField(blank=False)
    account = models.CharField(blank=True)
    number_buy = models.FloatField(blank=False)
    price_buy_sold = models.FloatField(blank=False)
    date_buy_sold = models.DateTimeField(default=timezone.now)
    #API:
    api_know = models.BooleanField(default=True)
    type = models.CharField(max_length=50, null=True, blank=True)
    company = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    sector = models.CharField(max_length=100, null=True, blank=True)
    industry = models.CharField(max_length=100, null=True, blank=True) #Technologie / Santé / Finance / Énergie / Matériaux de base / Industrie / Consommation cyclique/ Consommation non cyclique/ Télécommunications / Immobilier/ Services publics / Commodities / Gold
    ticker = models.CharField(max_length=10, unique=True)
    #information de l'user spécifique à une obligation
    maturity = models.DateTimeField()
    par_value = models.FloatField() #valeur nominale
    coupon = models.FloatField()
    frequency = models.CharField(choices=FrequencyList.choices,blank=True)


    def __str__(self):
        return f'{self.user}{self.name}'
    '''@transaction.atomic
        def maj_amount(self):
            Je viens mettre à jour ce pf dès qu'une nouvelle valeur vient s'y ajouter depuis la date à laquelle elle a été achetée on vient valoriser les valeurs par celle achetées
            S'il fait une requete get on vient mettre à jour la dernière valeur et si plus d'un mois sans maj on vient aussi faire une deuxième maj pour comble la différence entre les deux majs.

    '''

    '''@transaction.atomic
        def receive inf about api(self):
        - si certaine info ne sont pas donné par l'user comme catégorie etc alors je les récupère auprès de l'API.
    '''

class RealEstate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField(default=timezone.now)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    '''@transaction.atomic
        def maj_amount(self):
            Je viens mettre à jour ce pf dès qu'une nouvelle valeur vient s'y ajouter depuis la date à laquelle elle a été achetée on vient valoriser les valeurs par celle achetées
            S'il fait une requete get on vient mettre à jour la dernière valeur et si plus d'un mois sans maj on vient aussi faire une deuxième maj pour comble la différence entre les deux majs.

    '''
    '''@transaction.atomic
        def receive inf about api(self):
        - si certaine info ne sont pas donné par l'user comme catégorie etc alors je les récupère auprès de l'API.
    '''
class RealEstateDetail(models.Model):
    class EstateTypes(models.TextChoices):
        Appartement = 'Appartement',
        Maison = 'Maison',
        Garage = 'Garage',
        Commerce = 'Commerce',
        Bureau = 'Bureau', 
        Immeuble = 'Immeuble',
        Agricole = 'Agricole', 
        Autre = 'Autre',
    
    class OwnTypes(models.TextChoices): 
        Indivision = 'Indivision',
        SCI = 'SCI',
        Societe = 'Societe',
        Propre = 'Propre',
        Autre = 'Autre',
    
    class DestinationChoices(models.TextChoices): 
        RP = 'RP',
        RS = 'RS',
        Location = 'Location'

    class rentChoices(models.TextChoices):
        Vide = 'Vide',
        LMNP = 'LMNP',
        LMP = 'LMP',
    
    #Foreignkey
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #info d'origine
    type = models.CharField(choices = EstateTypes.choices)
    addresse = models.TextField()
    buy_date = models.DateTimeField()
    buy_price = models.IntegerChoices()
    sell_date = models.DateTimeField()
    sell_price = models.IntegerChoices()
    sell_date = models.DateTimeField()
    travaux_value = models.FloatField()
    other_costs = models.FloatField()
    notaire_costs = models.FloatField()
    apport = models.IntegerChoices()
    destination=models.CharField(choices=DestinationChoices.choices)
    #location
    type_rent = models.CharField(choices=rentChoices.choices)
    defisc = models.BooleanField(default=False)
    loyer_annuel = models.FloatField()
    charges_annuel = models.FloatField()
    Taxe = models.FloatField()
    #emprunt 
    emprunt_costs = models.FloatField()
    rate = models.FloatField()
    duration = models.IntegerField()
    #valeur saisie par l'user
    actual_value = models.FloatField()
    actual_date = models.DateTimeField(default=timezone.now)
    #propriété
    type_own = models.CharField(choices=OwnTypes.choices)
    part_own = models.IntegerField()




#ici je vais stocker tous les anciennes valeurs des actifs
    #fonction
        # Pour les actifs maj par l'api ils sont stocké qu'une fois puis supprimer avant d'être remaj
        # Pour les actifs maj par l'user ils sont stockés de manière permanante
class HistoricalPrice(models.Model):



    '''
        Je peux aussi recalculer les dividendes percus : 
        ticker = yf.Ticker("AAPL")  # Par exemple, pour Apple
        dividends = ticker.dividends
        print(dividends)
        for date, dividend in dividends.items():
        # Par exemple, le calcul des parts supplémentaires en fonction du dividende perçu
        parts = dividend / current_stock_price_on_date
        total_parts += parts
    '''


'''
Ici l'user peut modifier les données saisies par automatique de Assets exemple : 
- Country 
- Sector 
- etc 
mais ne dois pas affecter asset pour ne pas affecter les autres users 
'''
'''
Toutes les assets non gérés par yfinance ne doivent pas être envoyé vers assets pour éviter d'avoir en public des infos comme de l'immo ou autre'''