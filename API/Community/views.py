from django.shortcuts import render
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import SubjectDetailSerializer, SubjectListSerializer, FavoriSerializer, MessageSerializer, KeyWordSerializer
from .models import Subject, Message, KeyWord, Favori
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import authentication, exceptions, viewsets
from rest_framework import generics, views, status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import LimitOffsetPagination
from django.utils import timezone
from django.conf import settings

'''
Subject : 
    List : 
        - trier du plus au moins populaire
        - avoir tous les mots clés
        - essayer de récupérer les sujets créer par l'user
    Detail : 
        - récupère le sujet 
    Post : 
        - essayer de créer un sujet 
        - essayer de créer un sujet avec le même titre qu'un autre : error
        - essayer de créer un sujet avec les mêmes keyword : 200
Favori : 
        - essayer de créer des sujets favoris 
        - essayer de récupérer les sujets favoris de l'user 
message : 
    post : 
        - envoyer un message 
        - envoyer un message avec un fichier 
    get : 
        - récupérer les 10 derniers messages 
        - récupérer les 20 derniers messages
        '''

# Get and research subjects
class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Subject.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return SubjectListSerializer
        if self.action == 'retrieve':
            return SubjectDetailSerializer
        return super().get_serializer_class()
    
    def get_queryset(self):
        # Trier les sujets par nombre de messages hebdomadaires décroissant
        return Subject.objects.order_by('-weekly_messages')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Construction des résultats avec les mots-clés
        result = []
        for subject in serializer.data:
            subject_instance = Subject.objects.get(id=subject['id'])
            keywords = KeyWord.objects.filter(subject=subject_instance)
            keywords_serializer = KeyWordSerializer(keywords, many=True)
            
            # Extraire uniquement les mots-clés dans une liste
            keyword_list = [kw['keyword'] for kw in keywords_serializer.data]

            # Ajouter les sujets et leurs mots-clés associés dans le résultat final
            result.append({
                'subject': subject,
                'keywords': keyword_list
            })

        return Response(result)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class GetCreateSubjectAPIView(APIView):
    permisssion_classes = [IsAuthenticated]
    serializer_class = SubjectListSerializer

    def get(self, request):
        user = request.user
        subjects = Subject.objects.filter(created_user=user)
        serializer = SubjectListSerializer(subjects, many=True)
        return Response(serializer.data, status=200)
    
# subject (Post, Get only)
class CreateSubjectAPIView(APIView): 
    permission_classes = [IsAuthenticated]
    serializer_class = SubjectListSerializer
    
    def post(self, request):
        serializer = SubjectListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_user = request.user)
        return Response(serializer.data, status=201)
    

# follow subject 
class FavoriAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = FavoriSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)
    
    def get(self,request):
        user = request.user
        favoris = Favori.objects.filter(user = user)
        serializer = FavoriSerializer(favoris, many=True)
        return Response(serializer.data, status=200)
    
# send message
class MessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, subject_id): 
        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response({'error': 'Subject not found'}, status=404)
        
        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, subject=subject)
        return Response(serializer.data, status=201)

#Get Messages for 1 subject by pagination : 
class MessagePagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

class SubjectMessagesAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    pagination_class = MessagePagination

    def get_queryset(self):
        subject_id = self.kwargs.get('subject_id')
        return Message.objects.filter(subject__id=subject_id).order_by('-date')