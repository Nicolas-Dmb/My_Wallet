from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from rest_framework import routers
 
from User.views import UserViewset, SettingViewset, OTPAPIView
 

router = routers.SimpleRouter()

router.register('user', UserViewset, basename='user')
router.register('setting', SettingViewset, basename='setting' )

urlpatterns = [
    path('api/', include(router.urls)),
    path("admin/", admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/otp/', OTPAPIView.as_view(), name='OTP'),
]



