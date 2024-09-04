from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import AssetDetailSerializer, AssetListSerializer, AssetCreateSerializer
from .models import Asset, OneYearValue, OldValue
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics, views, status
from rest_framework.views import APIView
from django.conf import settings
import openai
import yfinance as yf


# Create your views here.

'''
- asset : 
    - get list
    - get detail
        - OneYearValue
        - OldValue
    - post (ticker)
        - in chatgpt search ticker
    - quick search ticker
'''
"View know ticker"
"une vue en liste qui permet de rechercher dans asset" 
"une requete qui permet de rechercher dans yfinance elle permet de créer de nouveaux assets et à l'user de rechercher de nouveaux assets"

def get_ticker(info):
    openai.api_key = settings.Chatgpt_Key

    try:
        completion = openai.Completion.create(
            model="gpt-4", 
            prompt=f"Write only the name of ticker in yfinance corresponding with this information: {info}. If any ticker corresponds, return them with spaces between; if none, return 'false'. If there is more than one ticker, return tickers separated by spaces.",
            max_tokens=50,  # Augmente la limite pour gérer plusieurs tickers
            temperature=0.0  # Réduit la créativité pour des réponses plus précises
        )
        
        response_text = completion.choices[0].text.strip()
        
        # Vérifiez si la réponse est 'false'
        if response_text.lower() == 'false':
            return False
        
        # Divisez les tickers par espace
        tickers = response_text.split()
        return tickers
    
    except Exception as e:
        print(f"Error: {e}")
        return None
    

class AssetViewset(ModelViewSet): 
    queryset = Asset.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve': 
            return AssetDetailSerializer
        elif self.action == 'list':
            return AssetListSerializer

    #si l'user clique sur un actif de son wallet suivie par yfinance 
    #ou sur un nouvelle asset dans la barre de recherche mais qui est déjà enregistré dans asset 
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        #on met à jour l'asset et ses historiques
        instance.maj_asset()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    #on créer l'asset à partir du moment ou l'user créer un nouveau asset pour son wallet (passe par wallet qui envoie vers asset)
    #ou que l'user clic sur une vue de détail d'un asset non encore suivie
    #si l'user le détermine en favoris
    def create(self, request, *args, **kwargs):
        response = Asset.create_asset(self,request.data['ticker'])

        if response == True:
            try:
                # Création des valeurs associées
                response_OneYear = OneYearValue.create_OneYearValue(self,request.data['ticker'])
                if response_OneYear == True :
                    response_OldValue = OldValue.create_OldValue(self,request.data['ticker'])
                
                # Si l'une des créations échoue, supprimer l'asset et lever une erreur
                if response_OneYear == False or response_OldValue == False:
                    Asset.objects.get(ticker=request.data['ticker']).delete()
                    return Response({"error": "Failed to create associated values"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Retourner l'asset créé avec les valeurs associées
                asset = Asset.objects.get(ticker=request.data['ticker'])
                serializer = AssetDetailSerializer(asset)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                # Suppression de l'asset en cas d'exception et renvoi d'une erreur
                Asset.objects.get(ticker=request.data['ticker']).delete()
                return Response({"error": f"Error during asset creation: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        elif response == 'Asset already exist':
            asset = Asset.objects.get(ticker=request.data['ticker'])
            asset.maj_asset()
            serializer = AssetDetailSerializer(asset)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return Response({"error": response}, status=status.HTTP_400_BAD_REQUEST)
# il permettra via la barre de recherche d'obtenir d'autres subjections d'assets 
# qui ne sont pas encore enregistrés dans Asset
class SearchOtherAssetsAPIView(APIView):

    def get(self, request, format=None):

        info = request.query_params.get('name')
        if not info:
            return Response({'error': 'le paramètre name est nécessaire'}, status=status.HTTP_400_BAD_REQUEST)
        
        tickers = get_ticker(info)
        if not tickers :
            return Response({'error': 'aucun token correspondant'}, status=status.HTTP_400_BAD_REQUEST)
        return_data = []
        for ticker in tickers : 
            ticker_info = yf.Ticker(ticker)
            if ticker_info.info is None or ticker_info.history(period="1d").empty:
                data = {
                    'ticker':ticker,
                    'error': 'No data available'
                }
            else : 
                data = {
                    'ticker': ticker,
                    'company': ticker_info.info('shortName',None),
                    'type': ticker_info.info('quoteType',None),
                    'country': ticker_info.info('country', None),
                }
            return_data.append(data)

        return Response(return_data, status=200)
            
            
        


