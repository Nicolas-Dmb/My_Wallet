from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Subject, Message, KeyWord, Favori
from rest_framework.validators import UniqueTogetherValidator


'''
Je veux que ca retour :
    pour SubjectList : 
        - titre 
        - l'user qui l'a crée
        - la liste des keywords 
        - envoie aussi l'activité en nombre de message/week
    pour SubjectDetail :
        - titre 
        - description
        - created_user
        - created_date
        - l'user qui l'a crée
            - la liste des keywords 
    GetMessage : Pagination
    - la liste des messages 
                - text
                - file
                - user
                - date
    pour les messages : 
        # pas liste de 10 messages : 
            - text
            - file
            - user
            - date
    pour les favoris : 
        - la liste des sujet
            - titre
    '''
class MessageSerializer(ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model= Message
        fields = ['text','file','username','date','subject']

    def create(self, validated_data):
        message = Message.objects.create(**validated_data)
        message.subject.count_message()
        return message

class SubjectListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='created_user.username', read_only=True)
    weekly_activity = serializers.SerializerMethodField()
    keywords = serializers.CharField(write_only=True)
    description = serializers.CharField(write_only=True)

    class Meta:
        model = Subject
        fields = ['title', 'username', 'keywords', 'weekly_activity', 'description']
        validators = [
            UniqueTogetherValidator(
                queryset=Subject.objects.all(),
                fields=['title'],
                message="Ce titre existe déjà"
            )
        ]

    def validate_description(self, value):
        # Validation de la description si nécessaire
        return value

    def validate_keywords(self, value):
        # Validation et transformation des mots-clés en liste
        return [keyword.strip().lower() for keyword in value.split(',')]

    def create(self, validated_data):
        # Extraire les mots-clés du validated_data
        keywords = validated_data.pop('keywords', [])

        # Créer le sujet
        subject = Subject.objects.create(**validated_data)

        # Créer les mots-clés associés
        for keyword in keywords:
            KeyWord.objects.create(subject=subject, keyword=keyword)

        return subject
        
    def get_weekly_activity(self, obj):
        return obj.know_subject_activity()
    
class KeyWordSerializer(ModelSerializer):
    class Meta:
        model= KeyWord
        fields = ['subject','keyword']
    
class SubjectDetailSerializer(ModelSerializer):
    username = serializers.CharField(source='created_user.username', read_only=True)
    #keywords = serializers.SerializerMethodField()

    class Meta:
        model= Subject
        fields = ['title','description','username']
    #je le bloque ainsi que de la ligne juste au dessus car je ne pense pas avoir besoin de keyword ici 
'''
    def get_keywords(self, obj):
        # Retourne les mots-clés associés au sujet sous forme de liste
        return [keyword.keyword for keyword in obj.keyword.all()]
'''


class FavoriSerializer(ModelSerializer):
    class Meta:
        model= Favori
        fields = ['subject']




        


