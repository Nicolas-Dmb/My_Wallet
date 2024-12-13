from django.db import models
from django.conf import settings
from django.db import transaction
from API.General.models import Asset as Asset_data
from API.General.models import OneYearValue, OldValue
from datetime import timedelta, datetime
from django.utils import timezone
from django.utils.timezone import now

class Wallet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateField(auto_now=True)

    @transaction.atomic
    def maj_amount(self):
        try:
            Boursecategorie = Bourse.objects.get(wallet=self)
            Cryptocategorie = Crypto.objects.get(wallet=self)
            Cashcategorie = Cash.objects.get(wallet=self)
        except : 
            return "error sur les catégories"
        self.amount = 0
        self.date = timezone.now()
        self.amount = Boursecategorie.amount + Cryptocategorie.amount + Cashcategorie.amount
        try:
            estate = RealEstate.objects.get(wallet=self)
        except: 
            return "erreur lors de la récupération de RealEstate"
        print(f"passage dans wallet maj {estate.amount}")
        self.amount += estate.amount
        self.save()

    def __str__(self):
        return f"Wallet : {self.user}/{self.amount}"

class Categories(models.Model):
    class CateList(models.TextChoices): 
        Bourse = 'Bourse', 
        Crypto = 'Crypto',
        Cash = 'Cash', 
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    date = models.DateField(default=now)
    type = models.CharField(max_length=10, choices=CateList.choices, blank=False)

    class Meta:
        abstract = True

    def __str__(self):
        return f"Assets Bourse ou Crypto : {self.wallet}/{self.amount}"
    
    @transaction.atomic
    def maj_SubWallet(self, categorie):
        self.amount = 0
        if categorie == 'Bourse':
            try : 
                assets = Asset.objects.filter(wallet = self.wallet, category='Bourse')
            except :
                return "Aucun asset trouvé pour cette catégorie"
            for asset in assets:
                self.amount += (asset.actual_price * asset.number)
                if BourseDetail.objects.filter(asset=asset).exists():
                    detail = BourseDetail.objects.filter(asset=asset).first()
                    if detail.sous_category == "Action":
                        categorie.amount_action += (asset.actual_price * asset.number)
                    elif detail.sous_category == "ETF":
                        categorie.amount_etf += (asset.actual_price * asset.number)
                    elif detail.sous_category == "Forex":
                        categorie.amount_forex += (asset.actual_price * asset.number)
                    elif detail.sous_category == "Matieres_Premieres":
                        categorie.amount_matieres_premieres += (asset.actual_price * asset.number)
        elif categorie=='Crypto':
            try :
                assets = Asset.objects.filter(wallet = self.wallet, category='Crypto')
            except :
                return "Aucun asset trouvé pour cette catégorie"
            for asset in assets:
                self.amount += (asset.actual_price * asset.number)
                if CryptoDetail.objects.filter(asset=asset).exists(): 
                    detail = CryptoDetail.objects.filter(asset=asset).first()
                    if detail.sous_category == "BTC":
                        categorie.amount_btc += (asset.actual_price * asset.number)
                    elif detail.sous_category == "ETF":
                        categorie.amount_eth += (asset.actual_price * asset.number)
                    elif detail.sous_category == "Stablecoins":
                        categorie.amount_stablecoins += (asset.actual_price * asset.number)
                    elif detail.sous_category ==  "Altcoins":
                        categorie.amount_altcoins += (asset.actual_price * asset.number)
                    elif detail.sous_category == "NFT":
                        categorie.amount_nft += (asset.actual_price * asset.number)
        self.date = timezone.now()
        self.save()
        #On met à jour le montant du wallet
        wallet = Wallet.objects.get(id=self.wallet.id)
        wallet.maj_amount()

    '''@transaction.atomic
    def new_SubWallet(self, categorie, wallet):
        self.wallet = wallet
        self.type = categorie
        self.save()
        self.maj_SubWallet(categorie)'''

    @transaction.atomic
    def maj_Cash(self):
        self.amount =0 
        try : 
            cashs = CashDetail.objects.filter()
        except :
            return 'error'
        self.amount_pea = 0
        self.amount_cto = 0  
        self.amount_Ass_Vie = 0
        self.amount_CSL_LEP = 0
        self.amount_CC = 0
        self.amount_Livret_A = 0
        self.amount_autre = 0
        for cash in cashs:
            if cash.account == 'CTO':
                self.amount_cto = cash.amount
            elif cash.account == 'PEA':
                self.amount_pea = cash.amount
            elif cash.account == 'Ass_Vie':
                self.amount_Ass_Vie = cash.amount
            elif cash.account == 'CSL_LEP':
                self.amount_CSL_LEP = cash.amount
            elif cash.account == 'CC':
                self.amount_CC = cash.amount
            elif cash.account == 'Livret_A':
                self.amount_Livret_A = cash.amount
            elif cash.account == 'autre':
                self.amount_autre = cash.amount
            self.amount += cash.amount
        self.save()
        #On met à jour le montant du wallet
        wallet = Wallet.objects.get(id=self.wallet.id)
        wallet.maj_amount()

    '''@transaction.atomic
    def new_Cash(self, wallet):
        self.wallet = wallet
        self.type = 'Cash'
        self.save()
        self.maj_Cash()'''

    def __str__(self):
        return f"Cash : {self.wallet} / {self.bank} / {self.account}"

class Bourse(Categories):
    #sous catégories
    amount_action = models.FloatField(default=0)
    amount_etf = models.FloatField(default=0)
    amount_forex = models.FloatField(default=0)
    amount_obligation = models.FloatField(default=0)
    amount_matieres_premieres = models.FloatField(default=0)

    def __str__(self):
        return "Bourse sous comptes"

class Crypto(Categories):
    #sous catégories
    amount_btc = models.FloatField(default=0)
    amount_eth = models.FloatField(default=0)
    amount_nft = models.FloatField(default=0)
    amount_stablecoins = models.FloatField(default=0)
    amount_altcoins = models.FloatField(default=0)
    
    def __str__(self):
        return "Cryptos sous comptes"

#cash Account 
class Cash(Categories):
        #sous catégories
    amount_pea = models.FloatField(default=0)
    amount_cto = models.FloatField(default=0)    
    amount_Ass_Vie = models.FloatField(default=0)
    amount_CSL_LEP = models.FloatField(default=0)
    amount_CC = models.FloatField(default=0)
    amount_Livret_A = models.FloatField(default=0)
    amount_autre = models.FloatField(default=0)

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
    
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='assets')
    name = models.CharField(max_length=50)
    actual_price = models.FloatField()
    date_price = models.DateField(blank=True, null=True) #instance créer lors de l'actualisation d'un prix non pris en charge par Yfinance
    currency = models.CharField(max_length=10, default=CurrencyList.EUR, choices=CurrencyList.choices, blank=False)
    category = models.CharField(max_length=10, choices=CategoryList.choices, blank=False)
    number = models.FloatField(blank=False)
    #api
    api_know = models.BooleanField(default=True)
    company = models.CharField(null=True, blank=True, max_length=50)
    type = models.CharField(max_length=50, null=True, blank=True)
    ticker = models.CharField(max_length=20)
    #API spécifique bourse
    country = models.CharField(max_length=50, null=True, blank=True)
    sector = models.CharField(max_length=100, null=True, blank=True)

    #Permet de créer une classe enfant de Categorie
    @transaction.atomic
    def new_SubWallet(self):
        if self.category == 'Crypto':
            categorie = Crypto.objects.create(wallet=self.wallet, type='Crypto')
        else :
            categorie = Bourse.objects.create(wallet=self.wallet, type='Bourse')
        categorie.save()
        categorie.maj_SubWallet(categorie.type)

    @transaction.atomic
    def get_new_price(self):
        try : 
            info = Asset_data.objects.get(ticker=self.ticker)
            info.maj_asset()
        except : 
            return False
        HistoricalWallet.NewPrice(self.category,info.date_value,self.actual_price-info.last_value, self.wallet)
        self.actual_price = info.last_value
        self.date_price = info.date_value
        return True
    
    # dès qu'il y a un buy sur nouvel asset du wallet ca passe ici si API_know sinon par serializer
    @classmethod
    @transaction.atomic
    def new_asset(cls, ticker, number, name, wallet, date):
        try:
            info = Asset_data.objects.get(ticker=ticker)
            info.maj_asset()
            api_know = True
        except:
            return False

        asset = cls.objects.create(
            wallet=wallet,
            number=number,
            name=name,
            api_know=api_know,
            type=info.type if api_know else None,
            actual_price=info.last_value if api_know else None,
            currency=info.currency if api_know else None,
            category=info.category if api_know else None,
            ticker=ticker,
            country=info.country if api_know else None,
            sector=info.sector if api_know else None,
            company=info.company if api_know else None,
        )

        # Met à jour les wallets par catégorie
        HistoricalWallet.NewValue(asset.category, date, asset.actual_price * asset.number, asset, ticker, wallet)

        # Gestion des sous-catégories
        try:
            if asset.category == 'Crypto':
                categories = Crypto.objects.get(wallet=wallet)
            else:
                categories = Bourse.objects.get(wallet=wallet)
        except (Crypto.DoesNotExist, Bourse.DoesNotExist):
            asset.new_SubWallet()
            return True
        categories.maj_SubWallet(asset.category)
        return True
    
    #Si buy ou sell 
    # ou si une information de cryptodetail ou boursedetail à changer 
    # ou si on veut connaitre les valeurs actualisée de l'asset
    @transaction.atomic
    def maj_asset(self, number, date):
        self.number += number
        try : 
            info = Asset_data.objects.get(ticker=self.ticker)
            info.maj_asset()
        except : 
            self.api_know = False
            return "Aucune donnée récupéré auprès de l'API"
        if number!=0:
            HistoricalWallet.NewValue(self.category,date,self.actual_price*self.number,self, self.ticker,self.wallet)
        else:
            HistoricalWallet.NewPrice(self.category,date,self.actual_price-info.last_value, self.wallet)
        self.actual_price = info.last_value
        self.save()
        # On vient mettre a jour les wallets par catégories
        try:
            if self.category == 'Crypto':
                categories = Crypto.objects.get(wallet=self.wallet)
            else :
                categories = Bourse.objects.get(wallet=self.wallet)
        except:
            self.new_SubWallet()
            return
        categories.maj_SubWallet(self.category)
        return

    
    #MAJ sans Yfinance
    @transaction.atomic
    def maj_asset_withoutAPI(self, actual_price, date,number=0):
        if date == None : date = timezone.now().date()
        if number!=0:
            HistoricalWallet.NewValue(self.category,date,float(actual_price)*float(self.number),self,self.ticker,self.wallet)
        elif actual_price: 
            HistoricalWallet.NewPrice(self.category,date,float(self.actual_price)-float(actual_price), self.wallet)
        #met à jour l'historique
        HistoricalPrice.objects.create(wallet=self.wallet,asset=self, date=self.date_price, value=self.actual_price)
        if(date>self.date_price):
            self.actual_price = actual_price
            self.date_price = date
        self.number += number
        self.save()
        # On vient mettre a jour les wallets par catégories
        try:
            if self.category == 'Crypto':
                categories = Crypto.objects.get(wallet=self.wallet)
            else:
                categories = Bourse.objects.get(wallet=self.wallet)
        except:
            self.new_SubWallet()
            return
        categories.maj_SubWallet(self.category)
        return
    #create sans Yfinance :
    @classmethod
    @transaction.atomic
    def create_asset_withoutAPI(cls ,wallet, name, type, price_buy, currency, categories, country, sector, company, ticker, date, number):
        asset = cls.objects.create(
            wallet = wallet,
            api_know = False,
            name = name,
            type = type,
            actual_price = price_buy,
            currency = currency,
            category = categories,
            ticker = ticker,
            country = country,
            sector = sector,
            company = company,
            number = number,
            date_price = date,
        )
        #on créer un historique 
        HistoricalWallet.NewValue(asset.category,date,price_buy*asset.number,asset,ticker,wallet)
        # On vient mettre a jour les wallets par catégories
        try:
            if asset.category == 'Crypto':
                categories = Crypto.objects.get(wallet=asset.wallet)
            else :
                categories = Bourse.objects.get(wallet=asset.wallet)
        except:
            asset.new_SubWallet()
            return 
        categories.maj_SubWallet(asset.category)
        return


#uniquement entre bourse et crypto
class Buy(models.Model):
    class CurrencyList(models.TextChoices): 
        EUR = 'EUR', 
        USD = 'USD',
        GBP = 'GBP',
        JPY = 'JPY',
    
    currency = models.CharField(max_length=10, default=CurrencyList.EUR, choices=CurrencyList.choices, blank=False)
    #Foreignkey
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='buy')
    #buy
    name = models.CharField(max_length=50)
    plateforme = models.CharField(blank=True, null=True,max_length=50)
    account = models.CharField(blank=True, null=True,max_length=100)
    number_buy = models.FloatField(blank=False)
    price_buy = models.FloatField(blank=False) #C'est le total et non l'unité
    date_buy = models.DateField(default=now)
    #API
    ticker = models.CharField(max_length=20)

    #dès que buy est créer et que cryptoDetail ou bourseDetail a été initialisé je dois appeler cette fonction pour initialiser asset puis wallet de la catégorie puis Wallet
    @transaction.atomic
    def new_buy(self, type='undifined', categories='undifined', country='undifined', sector='undifined', company='undifined'):
        #On vient mettre à jour Asset
        asset = Asset.objects.filter(ticker=self.ticker, wallet=self.wallet).first()
        if asset:
            if asset.api_know:
                asset.maj_asset(self.number_buy,self.date_buy)
            elif asset.date_price > self.date_buy :
                #si date de l'achat plus récent que sur asset 
                asset.maj_asset_withoutAPI(self.price_buy, self.date_buy, self.number_buy)
            else:
                asset.maj_asset_withoutAPI(asset.actual_price, self.date_buy,self.number_buy)
        else : #pour les asset à créer
            response = Asset.new_asset(self.ticker, self.number_buy, self.name, self.wallet, self.date_buy)
            if response == False:#pour les asset dont l'api ne met pas à jour
                Asset.create_asset_withoutAPI(self.wallet, self.name, type, self.price_buy, self.currency, categories, country, sector, company, self.ticker, self.date_buy, self.number_buy)
            
    def __str__(self):
        return f"Buy : {self.wallet} / {self.name} / {self.ticker}"

class Sells(models.Model):
    class CurrencyList(models.TextChoices): 
        EUR = 'EUR', 
        USD = 'USD',
        GBP = 'GBP',
        JPY = 'JPY',

    #identification
    name = models.CharField(max_length=50)
    ticker = models.CharField(max_length=20, unique=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='sells')
    #informations
    plateforme = models.CharField(blank=True, null=True,max_length=50)
    account = models.CharField(blank=True, null=True,max_length=50)
    currency = models.CharField(max_length=20, default=CurrencyList.EUR, choices=CurrencyList.choices, blank=False)
    number_sold = models.FloatField(blank=False)
    price_sold = models.FloatField(blank=False) #C'est le total et non l'unité
    date_sold = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Buy : {self.wallet} / {self.name} / {self.ticker}"
    
    #dès que sells est créer et que cryptoDetail ou bourseDetail a été initialisé je dois appeler cette fonction pour initialiser asset puis wallet de la catégorie puis Wallet
    @transaction.atomic
    def new_sell(self, type='undifined', categories='undifined', country='undifined', sector='undifined', company='undifined'):
        #On vient mettre à jour Asset
        asset = Asset.objects.filter(ticker=self.ticker, wallet=self.wallet).first()
        if asset:
            if asset.api_know:
                asset.maj_asset(self.number_sold*-1, self.date_sold) #in envoie le nombre en négatif
            else:
                asset.maj_asset_withoutAPI(self.price_sold, self.date_sold, (self.number_sold*-1))
        else:
            response = Asset.new_asset(self.ticker, self.number_sold*-1, self.name, self.wallet, self.date_sold)
            if response == False:
                Asset.create_asset_withoutAPI(self.wallet,False, self.name, type, self.price_sold*-1, self.currency, categories, country, sector, company, self.ticker, self.date_sold, self.number_sold)

        

class CryptoDetail(models.Model):
    class CategoryList(models.TextChoices):
        BTC = 'BTC'
        ETH = 'ETH'
        Stablecoins = 'Stablecoins'
        Altcoins = 'Altcoins'
        NFT = 'NFT'
    
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    #action
    sous_category = models.CharField(max_length=20, choices=CategoryList.choices, blank=False)
    stacking = models.BooleanField(default=False)
    number_stacking = models.IntegerField(blank=True, null=True)

    def __str__(self): 
        return f'Crypto Detail : {self.asset}'

class BourseDetail(models.Model):
    class FrequencyList(models.TextChoices):
        Annuelle = 'Annuelle'
        Semestrielle = 'Semestrielle'
        Trimestrielle = 'Trimestrielle'

    class CategoryList(models.TextChoices):
        Action = 'Action'
        ETF = 'ETF'
        Forex = 'Forex'
        Matieres_Premieres = 'Matieres_Premieres'

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    sous_category = models.CharField(max_length=20, choices=CategoryList.choices, blank=False)
    #API:
    industry = models.CharField(max_length=100, null=True, blank=True) #Technologie / Santé / Finance / Énergie / Matériaux de base / Industrie / Consommation cyclique/ Consommation non cyclique/ Télécommunications / Immobilier/ Services publics / Commodities / Gold

    def __str__(self): 
        return f'Crypto Detail : {self.asset}'

#cash Account 
class CashDetail(models.Model):
    class AccountTypes(models.TextChoices):
        PEA = 'PEA',
        CTO = 'CTO',
        Ass_Vie = 'Ass_Vie',
        CSL_LEP = 'CSL_LEP',
        CC = 'CC',
        Livret_A = 'Livret_A',
        autre = 'autre',

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    bank = models.CharField(max_length=50)
    account = models.CharField(max_length=50,choices=AccountTypes.choices, default=AccountTypes.CC)
    amount = models.FloatField(default=0)

    @transaction.atomic
    def new_Cash(self):
        categorie = Cash.objects.create(wallet=self.wallet, type='Cash')
        categorie.save()
        categorie.maj_Cash()

    @transaction.atomic
    def cash_maj_Amount(self, amount='undifined'):
        HistoricalPrice.objects.create(wallet=self.wallet,cash=self, date=timezone.now(), value=self.amount)
        if amount != 'undifined':
            HistoricalWallet.NewPrice('Cash',timezone.now(),self.amount-amount, self.wallet)
            self.amount += amount
            self.save()
        try:
            categorie = Cash.objects.get(wallet=self.wallet)
            categorie.maj_Cash()
        except:
            self.new_Cash()

class RealEstate(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    date = models.DateField(default=now)

    def __str__(self):
        return f'RealEstate : {self.wallet} / {self.amount}'
    
    #Dès qu'il y a une création ou maj sur RealEstateDetail on recalcule l'amount 
    @transaction.atomic
    def maj_amount(self):
        try :
            estates = RealEstateDetail.objects.filter(realestate=self)
        except:
            return "impossible de récupérer les données"
        self.amount=0
        for estate in estates:
            pret = estate.resteApayer
            valeur = estate.actual_value
            self.amount += (valeur-pret)
        self.save()
        #on met a jour le wallet 
        self.wallet.maj_amount()
            
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
    type = models.CharField(choices = EstateTypes.choices,max_length=50)
    adresse = models.TextField(blank=True, null=True)
    buy_date = models.DateField()
    buy_price = models.FloatField()
    sell_date = models.DateField(blank=True, null=True)
    sell_price = models.FloatField(blank=True, null=True)
    travaux_value = models.FloatField(blank=True, null=True)
    other_costs = models.FloatField(blank=True, null=True)
    notaire_costs = models.FloatField(blank=True, null=True)
    apport = models.FloatField(blank=True, null=True)
    destination=models.CharField(choices=DestinationChoices.choices, blank=True, null=True,max_length=50)
    #location
    type_rent = models.CharField(choices=rentChoices.choices, blank=True, null=True,max_length=50)
    defisc = models.BooleanField(default=False,blank=True, null=True)
    loyer_annuel = models.FloatField(blank=True, null=True)
    charges_annuel = models.FloatField(blank=True, null=True)
    taxe = models.FloatField(blank=True, null=True)
    #emprunt 
    emprunt_costs = models.FloatField(default=0)
    resteApayer=models.FloatField()
    rate = models.FloatField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    #valeur saisie par l'user
    actual_value = models.FloatField()
    actual_date = models.DateField(default=timezone.now().date())
    #propriété
    type_own = models.CharField(default='Propre',choices=OwnTypes.choices,max_length=50)
    part_own = models.IntegerField(blank=True, null=True)

    def __str__(self): 
        return f'RealEstate Detail: {self.realestate} / {self.type}'
    
    #maj historique value et RealEstateTotal
    @transaction.atomic
    def maj_realEstateDetail(self, actual_value='undifined', resteApayer='undifined'):
        if actual_value != 'undifined' and resteApayer != 'undifined':
            HistoricalWallet.NewPrice('Immo',timezone.now(),(self.actual_value-self.resteApayer)-(actual_value-resteApayer), self.realestate.wallet)
            HistoricalPrice.objects.create(wallet=self.realestate.wallet,RealEstate=self, date=self.actual_date, value=self.actual_value)
            self.actual_value = actual_value
            self.actual_date = timezone.now().date()
            self.resteApayer = resteApayer
        elif actual_value != 'undifined':
            HistoricalWallet.NewPrice('Immo',timezone.now(),(self.actual_value-self.resteApayer)-(actual_value-self.resteApayer), self.realestate.wallet)
            HistoricalPrice.objects.create(wallet=self.realestate.wallet,RealEstate=self, date=self.actual_date, value=self.actual_value)
            self.actual_value = actual_value
            self.actual_date = timezone.now().date()
        elif resteApayer != 'undifined':
            HistoricalWallet.NewPrice('Immo',timezone.now(),(self.actual_value-self.resteApayer)-(self.actual_value-resteApayer), self.realestate.wallet)
            self.resteApayer = resteApayer
        self.save()
        self.realestate.maj_amount()
        


#ici je vais stocker les anciennes valeurs d'actif non récupéré de yfiannce
class HistoricalPrice(models.Model):
    #Foreignkey
    wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE )
    cash = models.ForeignKey(CashDetail, on_delete=models.CASCADE, blank=True, null=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, blank=True, null=True)
    RealEstate = models.ForeignKey(RealEstateDetail, on_delete=models.CASCADE, blank=True, null=True)
    #Info
    date = models.DateField()
    value = models.FloatField()


#Historique des amounts des categories
class HistoricalWallet(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    date = models.DateField()
    value = models.FloatField()

    #dans le cas d'une mise à jour de prix d'un asset suivie ou non récent d'une semaine, alors on vient dans la fonction d'asset rajouter la différence de prix à la valeur de  HistoricalWallet et de la catégorie concernée

    #j'appelle le prix lors de buy ou sell
    #si l'achat :
        #- est déjà un asset en pf 
        #- non suivie 
        #- que cet achat est plus ancien que le prix initialisé dans asset 
        # => alors après l'initialisation de NewValue je dois aussi faire un NewPrice avec la date de asset du prix et le nouveau prix
    # value est le prix*nombre d'actif
    @transaction.atomic
    def NewValue(categorie,date,value,instance,ticker,wallet):
        if(isinstance(date,str)):
            date = datetime.strptime(date, "%Y-%m-%d").date()
        date_normalized = date - timedelta(days=date.weekday())
        if isinstance(date_normalized,datetime):
            date_normalized = date_normalized.date()
        while date_normalized < datetime.now().date(): # while date_normalized < datetime.now().date():
            #on séléctionne le prix 
            if Asset_data.objects.filter(ticker=ticker).exists():
                assetG = Asset_data.objects.get(ticker=ticker)
                #si la date_normalized est plus d'un an en arrière alors on récupère OldValue
                if date_normalized < datetime.now().date()- timedelta(days=365):
                    oldValue = OldValue.objects.filter(asset=assetG).order_by("-date").first()#on récupère la date la plus proche de date_normalized
                    value = oldValue.value
            else:
                #on selectionne le bon historicalPrice de la categorie
                match categorie:
                    case 'Cash':
                        self = HistoricalPrice.objects.filter(wallet=wallet,date__lte=date,cash=instance).order_by("-date").first()#on récupère la date la plus proche de date_normalized
                    case 'Bourse':
                        self = HistoricalPrice.objects.filter(wallet=wallet,date__lte=date,asset=instance).order_by("-date").first()#on récupère la date la plus proche de date_normalized
                    case 'Crypto':
                        self = HistoricalPrice.objects.filter(wallet=wallet,date__lte=date,asset=instance).order_by("-date").first()#on récupère la date la plus proche de date_normalized
                    case 'Immo':
                        self = HistoricalPrice.objects.filter(wallet=wallet,date__lte=date,RealEstate=instance).order_by("-date").first()#on récupère la date la plus proche de date_normalized
                #s'il n'est pas suivi et pas inscrit dans HistoricalPrice
                if self == None:
                    value = value
                else:#sinon
                    value = self.value
            #on selectionne le HistoricalWallet ou on en créer un 
            if HistoricalWallet.objects.filter(wallet=wallet,date = date_normalized).exists():
                historicalWallet = HistoricalWallet.objects.get(wallet=wallet,date = date_normalized)
                historicalWallet.value += value
                historicalWallet.save()
            else:
                HistoricalWallet.objects.create(wallet=wallet, date = date_normalized,value=value)
            #On selectionne sa souscatégorie et on y ajoute value
            match categorie:
                case 'Cash':
                    if HistoricalCash.objects.filter(wallet=wallet,date=date_normalized).exists():
                        sousHistorique = HistoricalCash.objects.get(wallet=wallet,date=date_normalized)
                        sousHistorique.value += value
                        sousHistorique.save()
                    else:
                        HistoricalCash.objects.create(wallet=wallet,date=date_normalized,value=value)
                case 'Bourse':
                    if HistoricalBourse.objects.filter(wallet=wallet,date=date_normalized).exists():
                        sousHistorique = HistoricalBourse.objects.get(wallet=wallet,date=date_normalized)
                        sousHistorique.value += value
                        sousHistorique.save()
                    else :
                        HistoricalBourse.objects.create(wallet=wallet,date=date_normalized,value=value)
                case 'Crypto':
                    if HistoricalCrypto.objects.filter(wallet=wallet,date=date_normalized).exists():
                        sousHistorique = HistoricalCrypto.objects.get(wallet=wallet,date=date_normalized)
                        sousHistorique.value += value
                        sousHistorique.save()
                    else:
                        HistoricalCrypto.objects.create(wallet=wallet,date=date_normalized,value=value)
                case 'Immo':
                    if HistoricalImmo.objects.filter(wallet=wallet,date=date_normalized).exists():
                        sousHistorique = HistoricalImmo.objects.get(wallet=wallet,date=date_normalized)
                        sousHistorique.value += value
                        sousHistorique.save()
                    else :
                        HistoricalImmo.objects.create(wallet=wallet,date=date_normalized,value=value)
            #date_normalized = date + timedelta(days=(7 - date.weekday()))
            date_normalized += timedelta(weeks=1)
            if isinstance(date_normalized,datetime):
                date_normalized = date_normalized.date()

    # lors d'un modif prix d'un asset non suivie dont le prix mis à jour est plus ancien qu'une semaine
    # value est la différence entre le nouveau et l'ancien prix * nombre d'actif
    @transaction.atomic
    def NewPrice(categorie,date,value, wallet):
        #ici je supprime l'ancien prix depuis sa nouvelle mise à jour 
        if date == None : 
            date = timezone.now().date()
        date_normalized = date - timedelta(days=date.weekday())
        if isinstance(date_normalized,datetime):
            date_normalized = date_normalized.date()
        while date_normalized < datetime.now().date():
            #on selectionne le HistoricalWallet ou on en créer un 
            historicalWallet = HistoricalWallet.objects.get(wallet=wallet,date = date_normalized)
            historicalWallet.value += value
            historicalWallet.save()
            #On selectionne sa souscatégorie et on y ajoute value
            match categorie:
                case 'Cash':
                    sousHistorique = HistoricalCash.objects.get(wallet=wallet,date=date_normalized)
                    sousHistorique.value += value
                    sousHistorique.save()
                case 'Bourse':
                    sousHistorique = HistoricalBourse.objects.get(wallet=wallet,date=date_normalized)
                    sousHistorique.value += value
                    sousHistorique.save()
                case 'Crypto':
                    sousHistorique = HistoricalCrypto.objects.get(wallet=wallet,date=date_normalized)
                    sousHistorique.value += value
                    sousHistorique.save()
                case 'Immo':
                    sousHistorique = HistoricalImmo.objects.get(wallet=wallet,date=date_normalized)
                    sousHistorique.value += value
                    sousHistorique.save()
            date_normalized = date + timedelta(days=(7 - date.weekday()))
            if isinstance(date_normalized,datetime):
                date_normalized = date_normalized.date()



class HistoricalCrypto(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    date = models.DateTimeField()
    value = models.FloatField()

class HistoricalBourse(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    date = models.DateTimeField()
    value = models.FloatField()

class HistoricalCash(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    date = models.DateTimeField()
    value = models.FloatField()

class HistoricalImmo(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    date = models.DateTimeField()
    value = models.FloatField()


    








'''
A Rajouter : 
'''
'''
    Dès qu'il y a un achat ou une vente sur un actif dont on précise l'origine de l'achat ca vient mettre a jour la valeur de ce model à la dernière date connue
'''
'''
    Calcul de dividende 
    Je peux aussi recalculer les dividendes percus : 
    ticker = yf.Ticker("AAPL")  # Par exemple, pour Apple
    dividends = ticker.dividends
    for date, dividend in dividends.items():
    # Par exemple, le calcul des parts supplémentaires en fonction du dividende perçu
    parts = dividend / current_stock_price_on_date
    total_parts += parts
'''
'''Calcul de stacking 
'''
''' Calcul de valorisation immo en fonction de l'emprunt à rembourser etc
'''

'''
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
'''
'''    
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

'''