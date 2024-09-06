from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import AssetDetailSerializer, AssetListSerializer, AssetCreateSerializer
from .models import Asset, OneYearValue, OldValue
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics, views, status
from rest_framework.views import APIView
from django.conf import settings
from openai import OpenAI
import yfinance as yf

client = OpenAI(api_key=settings.CHATGPT_KEY)



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

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Assurez-vous que le modèle est correct
            messages = [
                {"role": "system", "content": "You are an assistant that helps find tickers for assets listed on yfinance."},
                {
                    "role": "user",
                    "content": f"Find the ticker(s) in yfinance corresponding to this information(s): '{info}'. The information can refer to stocks, indices, ETFs, or cryptocurrencies, companys, ISIN and can be right in english or french. If no ticker matches, return 'false'. If multiple tickers match, return them separated by '/'. Only provide the tickers listed in yfinance without any additional information."
                }
                ],
            max_tokens=50,  # Augmente la limite pour gérer plusieurs tickers
            temperature=0.0  # Réduit la créativité pour des réponses plus précises
        )

        if not response or not response.choices[0].message.content:
            return "La requête à ChatGPT à échouée :"
        response_text = response.choices[0].message.content.strip()

        # Vérifiez si la réponse est 'false'
        if response_text.lower() == 'false':
            return False

        # Divisez les tickers par espace
        tickers = response_text.split('/')
        return tickers

    except Exception as e:
        return f"Error: La requête à ChatGPT à échouée : {e}"


class AssetViewset(ModelViewSet): 
    queryset = Asset.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve': 
            return AssetDetailSerializer
        elif self.action == 'list':
            return AssetListSerializer
        return AssetCreateSerializer

    #si l'user clique sur un actif de son wallet suivie par yfinance 
    #ou sur un nouvelle asset dans la barre de recherche mais qui est déjà enregistré dans asset 
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        #on met à jour l'asset et ses historiques
        response = instance.maj_asset()
        #on traite les différents retours possibles
        if isinstance(response, bool):
            if response == False:
                return Response({"error":"Impossible de mettre à jour l'actif"}, status=status.HTTP_400_BAD_REQUEST)
            elif response == True:
                serializer = self.get_serializer(instance)
                return Response(serializer.data, status=status.HTTP_200_OK)
        elif isinstance(response, str):
            if response == "asset doesn't exist":
                return Response({"error":"l'actif n'existe pas"}, status=status.HTTP_404_NOT_FOUND)
            elif "Erreur lors de la mise à jour de l'actif" in response : 
                return Response({"error":f"{response}"}, status=status.HTTP_400_BAD_REQUEST)
        #retour par défaut
        return Response("Erreur dans la mise à jour de l'actif", status=status.HTTP_404_NOT_FOUND)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    #on créer l'asset à partir du moment ou l'user créer un nouveau asset pour son wallet (passe par wallet qui envoie vers asset)
    #ou que l'user clic sur une vue de détail d'un asset non encore suivie
    #si l'user le détermine en favoris
    def create(self, request, *args, **kwargs):
        ticker = request.data['ticker'].upper()
        response = Asset.create_asset(self,ticker)

        if response == True:
            try:
                # Création des valeurs associées
                response_OneYear = OneYearValue.create_OneYearValue(self,ticker)
                if response_OneYear != True :
                    return Response({"error": f"{response_OneYear}"}, status=status.HTTP_400_BAD_REQUEST)
                response_OldValue = OldValue.create_OldValue(self,ticker)

                # Si l'une des créations échoue, supprimer l'asset et lever une erreur
                if response_OldValue == False:
                    Asset.objects.get(ticker=ticker).delete()
                    return Response({"error": f"{response_OldValue}"}, status=status.HTTP_400_BAD_REQUEST)

                # Retourner l'asset créé avec les valeurs associées
                asset = Asset.objects.get(ticker=ticker)
                serializer = AssetDetailSerializer(asset)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                # Suppression de l'asset en cas d'exception et renvoi d'une erreur
                Asset.objects.get(ticker=ticker).delete()
                return Response({"error": f"Erreur lors de la création de {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        elif response == "Asset not available in yfinance" :
            return Response({"error":"actif inaccessible"}, status=status.HTTP_400_BAD_REQUEST)
        elif response == 'Asset already exist':
            asset = Asset.objects.get(ticker=ticker)
            asset.maj_asset()
            serializer = AssetDetailSerializer(asset)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return Response({"error": response}, status=status.HTTP_400_BAD_REQUEST)
# il permettra via la barre de recherche d'obtenir d'autres subjections d'assets 
# qui ne sont pas encore enregistrés dans Asset
class SearchOtherAssetsAPIView(APIView):

    def get(self, request, name=None, format=None):
        name = name.upper()
        if not name:
            return Response({'error': 'le paramètre name est nécessaire'}, status=status.HTTP_400_BAD_REQUEST)

        tickers = get_ticker(name)
        if not tickers :
            tickers = name
        if isinstance(tickers, str):
            tickers = [tickers]
        if 'échouée' in tickers[0]: 
            return Response({'error': f'{tickers}'}, status=status.HTTP_400_BAD_REQUEST)
        return_data = []
        for ticker in tickers : 
            ticker_info = yf.Ticker(ticker)
            try:
                info = ticker_info.info
            except Exception as e:
                # Gestion de l'erreur si la requête à yfinance échoue
                return_data.append({
                    'ticker': ticker,
                    'error': f'Erreur lors de la récupération des données pour {ticker}: {str(e)}'
                })
                continue
            if info.get('shortName')==None:
                data = {
                    'ticker':ticker,
                    'error': 'No data available'
                }
            else : 
                data = {
                    'ticker': ticker,
                    'company': info.get('shortName',None),
                    'type': info.get('quoteType',None),
                    'country': info.get('country', None),
                }
            #je me demande juste si je ne dois pas aussi faire une requete sur le nom retourné par l'user au cas ou chatgpt m'orienterai vers une mauvaise direction
            return_data.append(data)

        return Response(return_data, status=200)





