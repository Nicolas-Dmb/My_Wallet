
from typing import Iterable
from uuid import UUID
from General.models import Asset
from Wallet.models import BourseDetail, Wallet
from Wallet.search.model import SearchModel
from django.contrib.postgres.search import TrigramSimilarity
from Wallet.models import Asset as OwnedAsset
class SearchStock: 
    @classmethod
    def get(cls,input:str, wallet:Wallet)-> Iterable[SearchModel]:
        stocks = cls._find(input=input)
        
        return (cls._toSearchModel(stock, wallet) for stock in stocks)
    
    @classmethod
    def _find(cls, input:str)-> Iterable[Asset]:
        return Asset.objects.filter(category='Bourse').annotate(
            similarity=(
            TrigramSimilarity('ticker', input) +
            TrigramSimilarity('company', input) +
            TrigramSimilarity('isin_code', input)
        )
        ).filter(similarity__gt=0.3).order_by('-similarity')
    
    @classmethod
    def _isOwned(cls, stock:Asset, wallet:Wallet)-> bool:
        return OwnedAsset.objects.filter(ticker=stock.ticker, wallet=wallet).exists()
    
    @classmethod
    def _toSearchModel(cls,stock:Asset, wallet:Wallet)-> SearchModel:
        return SearchModel(
            id =UUID(int=stock.id),
            type = type.bourse,
            name = stock.company,
            key = stock.ticker,
            amount = stock.last_value,
            owned = cls._isOwned(stock, wallet),
            other = stock.country,
        )   