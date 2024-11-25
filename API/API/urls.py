from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from rest_framework import routers
 
from User.views import UserViewset, SettingViewset, OTPAPIView, MPOublieAPIView
from Community.views import SubjectMessagesAPIView, SubjectViewSet, CreateSubjectAPIView, FavoriAPIView, MessageAPIView, GetCreateSubjectAPIView
from General.views import SearchOtherAssetsAPIView, AssetViewset
from Wallet.views import BuyView, SellView, MajAsset,CashAccount, RealEstateView, DeleteSellView, DeleteBuyView
from Wallet.viewsGet import AmountCategories,ListAsset,ListActifPassif, historiqueAchatVente, RevenuAnnuelImmo, MomentumPF, AssetData, PerformanceGlobal

router = routers.SimpleRouter()

#User
router.register('user', UserViewset, basename='user')
router.register('setting', SettingViewset, basename='setting' )
#Community
router.register('subject', SubjectViewSet, basename='subject') #ReadOnly 
#AssetViewset
router.register('asset', AssetViewset, basename='asset')
#Wallet
router.register('cash', CashAccount, basename='cash') #Modifier supprimer ou créer ou récupérer les données de cashDetail

urlpatterns = [
    path('api/', include(router.urls)),
    path("admin/", admin.site.urls),
    #user
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/otp/', OTPAPIView.as_view(), name='OTP'),
    path('api/mpoublie/', MPOublieAPIView.as_view(), name='MPOublie'),
    #Community
    path('api/community/subjects/<int:subject_id>/messages/', SubjectMessagesAPIView.as_view(), name='subject-messages'),
    path('api/community/create_subject/', CreateSubjectAPIView.as_view(), name='create_subject'),
    path('api/community/favoris/', FavoriAPIView.as_view(), name='favoris_community'),
    path('api/community/send/<int:subject_id>/message/', MessageAPIView.as_view(), name='send_message'),
    path('api/community/ownsubjects/', GetCreateSubjectAPIView.as_view(), name='own-subjects'),
    #General
    path('api/general/<str:name>/', SearchOtherAssetsAPIView.as_view(), name='search_other_assets'),
    #Wallet 
    path('api/wallet/buy/', BuyView.as_view(), name='buy_asset'), #POST Crypto et Bourse
    path('api/wallet/sell/', SellView.as_view(), name='sell_asset'), #POST Crypto et Bourse
    path('api/wallet/delete/buy/<int:pk>/', DeleteBuyView.as_view(), name='delete_buy'), #Delete Buy
    path('api/wallet/delete/sell/<int:pk>/', DeleteSellView.as_view(), name='delete_sell'), #Delete sell
    path('api/wallet/maj/', MajAsset.as_view(), name='maj_asset'), #PATCH Asset sur Crypto et Bourse
    path('api/wallet/realestate/', RealEstateView.as_view(), name='new_realEstate'), #post ou patch ImmoDetail
    path('api/wallet/realestate/<int:pk>/', RealEstateView.as_view(), name='maj_realEstate'), #post ou patch ImmoDetail
    path('api/wallet/amounts/<string:categorie>/', AmountCategories.as_view(), name='get_amount_of_categories'), #Get amount of categorie ['crypto','course','cash','all']
    path('api/wallet/list/<string:categorie>/', ListAsset.as_view(), name="get_list_asset"), #Get list of asset  ['crypto','course','cash','immo']
    path('api/wallet/actifpassif/<string:categorie>/', ListActifPassif.as_view(), name="get_actif_passif"), #Get Actif/Passif ['immo','all']
    path('api/wallet/historique/transaction/<string:categorie>/', historiqueAchatVente.as_view(), name="get_historique_transaction"),# Historique des transaction ['crypto','bourse','immo','all']
    path('api/wallet/revenu/annuel/', RevenuAnnuelImmo.as_view(), name="get_revenu_annuel"),#get sur les revenus annualisés de l'immo
    path('api/wallet/momentum/<string:categorie>/', MomentumPF.as_view(), name="get_momentum"),#Momentum of categories ['crypto','course','all']:
    path('api/wallet/asset/<string:categorie>/<int:pk>/', AssetData.as_view(), name="get_info_asset"),#permet de récupérer toutes les données propre à un Asset (crypto, bourse, immo, cash)
    path('api/wallet/perf/<string:categorie>/', PerformanceGlobal.as_view(), name="Get_perf_categories"),#donne les historiques de prix soit all, soit crypto, bourse, cash ou immo 
]



