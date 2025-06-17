
from typing import Iterable
from uuid import UUID
from General.models import Asset
from Wallet.models import BourseDetail, Wallet
from Wallet.search.model import SearchModel
from django.contrib.postgres.search import TrigramSimilarity
from Wallet.models import Asset as OwnedAsset

class SearchCrypto: 
    @classmethod
    def get(cls,input:str, wallet:Wallet)-> Iterable[SearchModel]:
        cryptos = cls._find(input=input)
        
        return (cls._toSearchModel(crypto, wallet) for crypto in cryptos)
    
    @classmethod
    def _find(cls, input:str)-> Iterable[Asset]:
        return Asset.objects.filter(category='Crypto').annotate(
            similarity=(
            TrigramSimilarity('ticker', input) +
            TrigramSimilarity('company', input) +
            TrigramSimilarity('isin_code', input)
        )
        ).filter(similarity__gt=0.3).order_by('-similarity')
    
    @classmethod
    def _isOwned(cls, crypto:Asset, wallet:Wallet)-> bool:
        return OwnedAsset.objects.filter(ticker=crypto.ticker, wallet=wallet).exists()
    
    @classmethod
    def _toSearchModel(cls,crypto:Asset, wallet:Wallet)-> SearchModel:
        return SearchModel(
            id =UUID(int=crypto.id),
            type = type.crypto,
            name = crypto.company,
            key = crypto.ticker,
            amount = crypto.last_value,
            owned = cls._isOwned(crypto, wallet),
            other = crypto.country,
        )