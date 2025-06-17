from typing import Iterable
from uuid import UUID
from Wallet.models import CashDetail, Wallet
from Wallet.search.model import SearchModel
from django.contrib.postgres.search import TrigramSimilarity

class SearchCash:
    @classmethod
    def get(cls,input:str, wallet:Wallet)-> Iterable[SearchModel]:
        cashs = cls._find(input=input, wallet=wallet)
        
        return (cls._toSearchModel(cash) for cash in cashs)
    
    @classmethod
    def _find(cls, input:str,wallet:Wallet)-> Iterable[CashDetail]:
        return CashDetail.objects.filter(wallet=wallet).annotate(
            similarity=(
            TrigramSimilarity('bank', input) +
            TrigramSimilarity('account', input)
        )
        ).filter(similarity__gt=0.3).order_by('-similarity')
    
    @classmethod
    def _toSearchModel(cls,cash:CashDetail)-> SearchModel:
        return SearchModel(
            id =UUID(int=cash.id),
            type = type.cash,
            name = f"{cash.bank} - {cash.account}",
            key = None,
            amount = cash.amount,
            owned = True,
            other = None
        )   