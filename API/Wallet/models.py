from django.db import models
from django.conf import settings
from django.db import transaction
from django.utils import timezone

'''
test : 
    - si l'user ne saisie pas toutes les valeurs demandées
    - Dès qu'un user met une nouvelle valeur à l'achat ou la vente ca met à jour Asset puis 
    
'''

class Wallet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField(default=timezone.now)

    '''@transaction.atomic
        def maj_amount(self):
            A chaque nouvelle date je cumule les valeur de crypto/bourse/Immo/Cash et autre de l'user puis je créer un nouveau model wallet'''

    def __str__(self):
        return f"Wallet : {self.user}/{self.amount}"

class Categories(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

    def __str__(self):
        return f"Assets Bourse ou Crypto : {self.wallet}/{self.amount}"

class Bourse(Categories):
    #sous catégories
    amount_action = models.FloatField()
    amount_etf = models.FloatField()
    amount_forex = models.FloatField()
    amount_obligation = models.FloatField()
    amount_matières_premières = models.FloatField()

    def __str__(self):
        return "Bourse sous comptes"

class Crypto(Categories):
    #sous catégories
    amount_btc = models.FloatField()
    amount_eth = models.FloatField()
    amount_nft = models.FloatField()
    amount_stablecoins = models.FloatField()
    amount_altcoins = models.FloatField()
    
    def __str__(self):
        return "Cryptos sous comptes"
#cash Account 
class Cash(Categories):
    class AccountTypes(models.TextChoices):
        PEA = 'PEA',
        CTO = 'CTO',
        Ass_Vie = 'Ass_Vie',
        CSL_LEP = 'CSL_LEP',
        CC = 'CC', #compte courant 
        Livret_A = 'Livret_A',
        autre = 'autre',

    bank = models.CharField()
    account = models.CharField(choices=AccountTypes.choices, default=AccountTypes.CC)
    '''
    Dès que la date est mise à jour on créer un nouveau model avec la nouvelle amount et date
    '''
    '''
    Dès qu'il y a un achat ou une vente sur un actif dont on précise l'origine de l'achat ca vient mettre a jour la valeur de ce model à la dernière date connue
    '''
    def __str__(self):
        return f"Cash : {self.wallet} / {self.bank} / {self.account}"

# tous les assets uniques de l'user : 
class Asset(models.Model):
    class CategoryList(models.TextChoices):
        Crypto = 'Crypto'
        Bourse = 'Bourse'
    class CurrencyList(models.TextChoices): 
        EUR = 'EUR', 
        USD = 'USD',
        GBP = 'GBP',
        JPY = 'JPY',
    
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='buys')
    name = models.CharField()
    actual_price = models.FloatField()
    currency = models.CharField(max_length=10, default=CurrencyList.EUR, choices=CurrencyList.choices, blank=False)
    category = models.CharField(max_length=10, choices=CategoryList.choices, blank=False)
    number = models.FloatField(blank=False)
    #api
    api_know = models.BooleanField(default=True)
    type = models.CharField(max_length=50, null=True, blank=True)
    ticker = models.CharField(max_length=10)
    #API spécifique bourse
    company = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    sector = models.CharField(max_length=100, null=True, blank=True)

    '''
    Je dois récupérer de Buy et de Sold les infos envoyées par l'user comme : 
    - category
    - name
    Puis je dois mettre à jour le numbre de part détenue : 
    - sur buy et sold 
    '''

#uniquement entre bourse et crypto
class Buy(models.Model):
    class CurrencyList(models.TextChoices): 
        EUR = 'EUR', 
        USD = 'USD',
        GBP = 'GBP',
        JPY = 'JPY',
    
    currency = models.CharField(max_length=10, default=CurrencyList.EUR, choices=CurrencyList.choices, blank=False)
    #Foreignkey
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='buys')
    #buy
    name = models.CharField()
    plateforme = models.CharField(blank=False)
    account = models.CharField(blank=True)
    number_buy = models.FloatField(blank=False)
    price_buy = models.FloatField(blank=False)
    date_buy = models.DateTimeField(default=timezone.now)
    #API
    ticker = models.CharField(max_length=10)


    def __str__(self):
        return f"Buy : {self.wallet} / {self.name} / {self.ticker}"
    '''
    @transaction.atomic
        def maj_amounts(self):
            dès qu'un nouveau amount est saisie, je recalcul les amounts des sous catégories en prennant en compte les sells
    '''
    '''
    @transaction.atomic
        Envoyer total categories a other class(self):
        - Si un changement dans asset on vient refaire la somme de bourse/Crypto renvoyer la sum en prennant en compte les sells
    '''
    '''
    @transaction.atomic
        def receive inf about api(self):
        - si certaine info ne sont pas donné par l'user comme catégorie etc alors je les récupères auprès de l'API. 
    '''


class Sells(models.Model):
    class CategoryList(models.TextChoices):
        Crypto = 'Crypto'
        Bourse = 'Bourse'
    
    class CurrencyList(models.TextChoices): 
        EUR = 'EUR', 
        USD = 'USD',
        GBP = 'GBP',
        JPY = 'JPY',

    #identification
    name = models.CharField()
    ticker = models.CharField(max_length=10, unique=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='sells')
    #informations
    currency = models.CharField(max_length=10, default=CurrencyList.EUR, choices=CurrencyList.choices, blank=False)
    category = models.CharField(max_length=10, choices=CategoryList.choices, blank=False)
    number_sold = models.FloatField(blank=False)
    price_sold = models.FloatField(blank=False)
    date_sold = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Buy : {self.wallet} / {self.name} / {self.ticker}"

    '''
    @transaction.atomic
        def maj_amounts(self):
            dès qu'un nouveau amount est saisie, je recalcul les amounts des sous catégories en prennant en compte les sells
    '''
    '''
    @transaction.atomic
        Envoyer total categories a other class(self):
        - Si un changement dans asset on vient refaire la somme de bourse/Crypto renvoyer la sum en prennant en compte les sells
    '''
    '''
    @transaction.atomic
        def receive inf about api(self):
        - si certaine info ne sont pas donné par l'user comme catégorie etc alors je les récupères auprès de l'API. 
        Puis je les stockes dans les historiques.
    '''


class CryptoDetail(models.Model):
    class CategoryList(models.TextChoices):
        BTC = 'BTC'
        ETH = 'ETH'
        Stablecoins = 'Stablecoins'
        Altcoins = 'Altcoins'
        NFT = 'NFT'
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    #action
    sous_category = models.CharField(max_length=10, choices=CategoryList.choices, blank=False)
    stacking = models.BooleanField(default=False)

    def __str__(self): 
        return f'Crypto Detail : {self.asset}'

class Stacking(models.Model):
    class FrequencyList(models.TextChoices):
        Year = 'Year'
        Month = 'Month'
        Week = 'Week'
        Day = 'Day'
        Hour = 'Hour'
        Minute = 'Minute'

    #Foreign_Key
    crypto = models.ForeignKey(CryptoDetail, on_delete=models.CASCADE)
    number = models.FloatField() # nombre de part en stacking
    #stacking
    stacking = models.BooleanField(default=False)
    rate_rewards = models.FloatField(default=0)
    rewards = models.CharField() #quel crypto est donnée en rewards
    last_reward_cal = models.DateTimeField()
    frequency = models.CharField(max_length=10, choices=FrequencyList.choices, blank=False)

    def __str__(self): 
        return f'Stacking : {self.crypto}'

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

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    sous_category = models.CharField(max_length=10, choices=CategoryList.choices, blank=False)
    #API:
    industry = models.CharField(max_length=100, null=True, blank=True) #Technologie / Santé / Finance / Énergie / Matériaux de base / Industrie / Consommation cyclique/ Consommation non cyclique/ Télécommunications / Immobilier/ Services publics / Commodities / Gold

    def __str__(self): 
        return f'Crypto Detail : {self.asset}'
    
class Obligation(models.Model):
    class FrequencyList(models.TextChoices):
        Annuelle = 'Annuelle'
        Semestrielle = 'Semestrielle'
        Trimestrielle = 'Trimestrielle'
    
    bourse = models.ForeignKey(BourseDetail, on_delete=models.CASCADE)
    #information de l'user spécifique à une obligation
    maturity = models.DateTimeField()
    par_value = models.FloatField() #valeur nominale
    coupon = models.FloatField()
    frequency = models.CharField(choices=FrequencyList.choices,blank=True)


    def __str__(self): 
        return f'Obligation : {self.bourse}'


class RealEstate(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f'RealEstate : {self.wallet} / {self.amount}'

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
    realestate = models.ForeignKey(RealEstate, on_delete=models.CASCADE)
    #info d'origine
    type = models.CharField(choices = EstateTypes.choices)
    addresse = models.TextField()
    buy_date = models.DateTimeField()
    buy_price = models.FloatField()
    sell_date = models.DateTimeField()
    sell_price = models.FloatField()
    travaux_value = models.FloatField()
    other_costs = models.FloatField()
    notaire_costs = models.FloatField()
    apport = models.FloatField()
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

    def __str__(self): 
        return f'RealEstate Detail: {self.realestate} / {self.type}'
    
    '''
    Action dès qu'une info est modifié sur detail real estate: 
    Calcul de la valeur (appot - emprunt -valeur du bien)'''

#ici je vais stocker tous les anciennes valeurs des actifs
    #fonction
        # Pour les actifs maj par l'api ils sont stocké qu'une fois puis supprimer avant d'être remaj
        # Pour les actifs maj par l'user ils sont stockés de manière permanante
class HistoricalPrice(models.Model):
    #Foreignkey
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, blank=True, null=True)
    RealEstate = models.ForeignKey(RealEstateDetail, on_delete=models.CASCADE, blank=True, null=True)
    #Info
    number = models.FloatField()
    date = models.DateTimeField()
    value = models.FloatField()
    sum = models.FloatField()








'''
A Rajouter : 
'''
'''Calcul de dividende 
    Je peux aussi recalculer les dividendes percus : 
    ticker = yf.Ticker("AAPL")  # Par exemple, pour Apple
    dividends = ticker.dividends
    print(dividends)
    for date, dividend in dividends.items():
    # Par exemple, le calcul des parts supplémentaires en fonction du dividende perçu
    parts = dividend / current_stock_price_on_date
    total_parts += parts
'''
'''Calcul de stacking 
'''
''' Calcul de valorisation immo en fonction de l'emprunt à rembourser etc
'''