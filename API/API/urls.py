from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from rest_framework import routers
 
from User.views import UserViewset, SettingViewset, OTPAPIView, MPOublieAPIView
from Community.views import SubjectMessagesAPIView, SubjectViewSet, CreateSubjectAPIView, FavoriAPIView, MessageAPIView, GetCreateSubjectAPIView

router = routers.SimpleRouter()

#User
router.register('user', UserViewset, basename='user')
router.register('setting', SettingViewset, basename='setting' )
#Community
router.register('subject', SubjectViewSet, basename='subject') #ReadOnly 

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
]



