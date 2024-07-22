from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import UserSerializer, SettingSerializer
from .models import User, Setting
from rest_framework.viewsets import ModelViewSet, APIView
from rest_framework import authentication, exceptions
from rest_framework import generics, views, status
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
import pyotp
from django.utils import timezone

'''
Test OTP : 
- demande de code avec le mail 
- demande de code sans être co et en étant co 
- demande de code OTP en ayant un déjà validé
- vérifier le code OTP après un délai trop long 
- vérifier le bon et le mauvais code OTP 
- Veifier le code otp alors que rien n'est transmis 
- véirier avec un code qui contient des lettres 
'''

class UserViewset(ModelViewSet): 
    serializer_class=UserSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)


class SettingViewset(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SettingSerializer

    def get_queryset(self, request):
        return Setting.objects.filter(user = request.user)

class OTPAPIView(APIView): 
    permission_classes = [IsAuthenticated]

    def get(self, request): 
        user = request.user
        try : 
            # On verifie qu'il n'y a pas déjà un otp valide : 
            if not user.OTP_Status():
                # Génération d'une clé secrète OTP
                secret_key = pyotp.random_base32()
                otp = pyotp.TOTP(secret_key)
                token = otp.now()

                # Envoi de l'email avec la clé OTP
                send_mail(
                    'Votre code OTP',
                    f'Votre code OTP est : {token}',
                    'securite@trackey.fr',
                    [f'{request.user.email}'],
                    fail_silently=False,
                )
                # Stockage de la clé OTP dans le modèle utilisateur et de la date de mise à jour
                user.otp_key = token
                user.otp_generate = timezone.now()
                user.save()            
                # Redirection vers une page où l'utilisateur peut saisir le code OTP
                return Response(status=status.HTTP_200_OK)
            else : 
                Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Error':e},status=status.HTTP_400_BAD_REQUEST)


    def post(self, request):
        user = request.user
        try :
            if user.otp_Status is not None : 
                # Récupération de la clé OTP soumise par l'utilisateur
                submitted_otp = request.data.get('otp')
                if submitted_otp is None or not submitted_otp.isdigit(): 
                    return Response({'error': 'code invalide'}, status=status.HTTP_400_BAD_REQUEST)
                # Récupération de la clé OTP associée à l'utilisateur
                stored_otp = user.otp_key
                valid_otp = user.otp_generate + timezone.timedelta(minutes=3)
                # Vérification si les clés OTP correspondent
                if int(submitted_otp) == int(stored_otp) and timezone.now() < valid_otp:
                    # Clé OTP valide, autoriser l'accès
                    user.email_verif = True
                    user.OTP_Set()
                    user.otp_key = None
                    user.otp_generate = None
                    user.save() 
                    return Response(status=status.HTTP_200_OK)
                elif timezone.now() > valid_otp:
                    # Clé OTP timeout :
                    user.otp_key = None
                    user.otp_generate = None
                    user.save()      
                    return Response({'error': 'délai écoulé'}, status=status.HTTP_408_REQUEST_TIMEOUT)
                elif submitted_otp != stored_otp :
                    # Clé OTP invalide : 
                    return Response({'error': 'code invalide'}, status=status.HTTP_400_BAD_REQUEST)
            else : 
                Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Error':e},status=status.HTTP_400_BAD_REQUEST)


