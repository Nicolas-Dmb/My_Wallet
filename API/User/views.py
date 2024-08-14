from django.shortcuts import render
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import UserSerializer, SettingSerializer, PasswordResetSerializer
from .models import User, Setting
from rest_framework.viewsets import ModelViewSet
from rest_framework import authentication, exceptions
from rest_framework import generics, views, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import send_mail
import pyotp
from django.utils import timezone
from django.conf import settings
from itsdangerous import URLSafeSerializer

class UserViewset(ModelViewSet): 
    serializer_class=UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    
    def perform_create(self, serializer):
        user = serializer.save()
        # Créer les paramètres de l'utilisateur après la création de l'utilisateur
        Setting.objects.create(user=user)


class SettingViewset(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SettingSerializer

    def get_queryset(self):
        return Setting.objects.filter(user = self.request.user)

class OTPAPIView(APIView): 
    permission_classes = [IsAuthenticated]

    def get(self, request): 
        user = request.user
        try : 
            # On verifie qu'il n'y a pas déjà un otp valide : 
            if user.OTP_Status() is False:
                valid_otp = user.otp_generate + timezone.timedelta(seconds=60)
                if timezone.now() < valid_otp:
                    return Response(status=status.HTTP_304_NOT_MODIFIED)
                # Génération d'une clé secrète OTP
                secret_key = pyotp.random_base32()
                otp = pyotp.TOTP(secret_key)
                token = otp.now()

                # Envoi de l'email avec la clé OTP
                send_mail(
                    'Votre code OTP',
                    f'Votre code OTP est : {token}',
                    'securite@trackey.fr',
                    [user.email],
                    fail_silently=False,
                )
                # Stockage de la clé OTP dans le modèle utilisateur et de la date de mise à jour
                user.otp_key = token
                user.otp_generate = timezone.now()
                user.save()
                # Redirection vers une page où l'utilisateur peut saisir le code OTP
                return Response(status=status.HTTP_201_CREATED)
            else : 
                # verif OTP n'est pas nécessaire car déjà fait il y a peu
                return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Error':str(e)},status=status.HTTP_400_BAD_REQUEST)


    def post(self, request):
        user = request.user
        try :
            if user.OTP_Status() is False : 
                # Récupération de la clé OTP soumise par l'utilisateur
                submitted_otp = request.data.get('otp')
                if submitted_otp is None: 
                    return Response({'error': 'Code invalide'}, status=status.HTTP_400_BAD_REQUEST)
                # Récupération de la clé OTP associée à l'utilisateur
                stored_otp = user.otp_key
                valid_otp = user.otp_generate + timezone.timedelta(seconds=60)
                # Vérification si les clés OTP correspondent
                if int(submitted_otp) == int(stored_otp) and timezone.now() < valid_otp:
                    # Clé OTP valide, autoriser l'accès
                    user.email_verif = True
                    user.OTP_Set()
                    user.otp_key = None
                    user.save() 
                    return Response(status=status.HTTP_200_OK)
                elif timezone.now() > valid_otp:
                    # Clé OTP timeout :
                    user.otp_key = None
                    user.save()
                    return Response({'error': 'délai écoulé'}, status=status.HTTP_408_REQUEST_TIMEOUT)
                elif submitted_otp != stored_otp :
                    # Clé OTP invalide : 
                    return Response({'error': 'code invalide'}, status=status.HTTP_400_BAD_REQUEST)
            else : 
                return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Error':str(e)},status=status.HTTP_400_BAD_REQUEST)

# Mot de passe oublié 
class MPOublieAPIView(APIView):

    def post(self, request):
        user_email = request.data.get('email')
        try : 
            user = User.objects.get(email=user_email)
        except : 
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        if user.email_verif == True:
            secret_key = settings.SECRET_KEY + user.username
            auth_s = URLSafeSerializer(secret_key, "auth")
            token = auth_s.dumps({"id":str(user.id) , "name": "MotDePasseOublie"})
            user.token = token
            user.date_token = timezone.now()
            user.save()
            send_mail(
                    'Mot de passe oublié',
                    'Vous avez fait une demande de réinitialisation de votre mot de passe.'
                    f'Cliquez sur ce lien pour en définir un nouveau : lien/{token}',
                    'securite@trackey.fr',
                    [f'{user.email}'],
                    fail_silently=False,)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Email non vérifié'}, status=status.HTTP_401_UNAUTHORIZED)

    def patch(self,request):
        token = request.data.get('token')
        try : 
            user = User.objects.get(token=token)
        except :
            return Response({'error': 'User not found'}, status=status.HTTP_408_REQUEST_TIMEOUT)
        try:
            #récupère l'id via la code donné et la validité du code
            secret_key = settings.SECRET_KEY + str(user.username)
            auth_s = URLSafeSerializer(secret_key, "auth")
            data = auth_s.loads(token)
            token_id = data["id"] 
            valid_token = user.date_token + timezone.timedelta(minutes=5)
            # vérifie l'id est bon et que le lien est toujours valide 
            if str(user.id) == token_id and timezone.now() < valid_token: 
                serializer = PasswordResetSerializer(data=request.data)
                if serializer.is_valid():
                    user.set_password(serializer.validated_data['password'])
                    user.token = None
                    user.date_token = user.date_token - timezone.timedelta(minutes=6)
                    user.save()
                    return Response(status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            user.token = None
            user.save()
            return Response({'error': 'token invalide'}, status=status.HTTP_408_REQUEST_TIMEOUT)
        except:
            user.token = None
            user.save()
            return Response({'error': 'token invalide'}, status=status.HTTP_408_REQUEST_TIMEOUT)
