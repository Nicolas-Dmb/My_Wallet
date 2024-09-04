from django.db import models

# Create your models here.
'''
User Asset 
- know_API ? '''


'''
Je peux aussi recalculer les dividendes percus : 
ticker = yf.Ticker("AAPL")  # Par exemple, pour Apple
dividends = ticker.dividends
print(dividends)
for date, dividend in dividends.items():
    # Par exemple, le calcul des parts supplémentaires en fonction du dividende perçu
    parts = dividend / current_stock_price_on_date
    total_parts += parts'''


'''
Ici l'user peut modifier les données saisies par automatique de Assets exemple : 
- Country 
- Sector 
- etc 
mais ne dois pas affecter asset pour ne pas affecter les autres users 
'''
'''
Toutes les assets non gérés par yfinance ne doivent pas être envoyé vers assets pour éviter d'avoir en public des infos comme de l'immo ou autre'''