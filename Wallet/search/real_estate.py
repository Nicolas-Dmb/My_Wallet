from typing import Iterable
from uuid import UUID
from Wallet.models import RealEstate, RealEstateDetail, Wallet
from Wallet.search.model import SearchModel
from django.contrib.postgres.search import TrigramSimilarity

class SearchRealEstate: 
    @classmethod
    def get(cls,input:str, wallet:Wallet)-> Iterable[SearchModel]:
        realEstate = cls._getOwnedRealEstate(wallet)
        realEstateDetails = cls._find(input=input, realestate=realEstate)
        
        return (cls._toSearchModel(realEstateDetail) for realEstateDetail in realEstateDetails)
    
    @classmethod
    def _getOwnedRealEstate(cls, wallet:Wallet) -> RealEstate:
        return RealEstate.objects.get(wallet=wallet)
    
    @classmethod
    def _find(cls, input:str,realestate:RealEstate)-> Iterable[RealEstateDetail]:
        return RealEstateDetail.objects.filter(realestate=realestate).annotate(
            similarity=TrigramSimilarity('adresse', input)
        ).filter(similarity__gt=0.3)
    
    @classmethod
    def _toSearchModel(cls,realEstateDetail:RealEstateDetail)-> SearchModel:
        return SearchModel(
            id =UUID(int=realEstateDetail.id),
            type = type.immo,
            name = f"{realEstateDetail.type} - {realEstateDetail.destination}",
            key = realEstateDetail.adresse,
            amount = realEstateDetail.actual_value,
            owned = True,
            other = None
        )   