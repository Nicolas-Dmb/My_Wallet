from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import UserSerializer
from .models import User, Setting
from rest_framework.viewsets import ModelViewSet
from rest_framework import authentication, exceptions
from rest_framework import generics, views, status
from rest_framework.permissions import IsAuthenticated


class UserViewset(ModelViewSet): 
    serializer_class=UserSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

#Settings
#OTP


