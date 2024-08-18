import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from datetime import timedelta
from django.test import TestCase
from .models import Subject, Favori, Message, KeyWord
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()

#compte créer, puis connecter, puis accès à des infos protégées. 
@pytest.fixture
def accounts_fixture():
    return [
        {
            "first_name": "Hugo",
            "last_name": "Dujardin",
            "username": "Hugo",
            "email": "Hugp@gmail.com",
            "phone": "00000000",
            "password": "12345Nano!",
            "confirm_password": "12345Nano!",
        },
        {
            "first_name": "Marie",
            "last_name": "Duparc",
            "username": "Marie",
            "email": "Marie@gmail.com",
            "phone": "00000001",
            "password": "12345Nano!",
            "confirm_password": "12345Nano!",
        },
        {
            "first_name": "Tom",
            "last_name": "Legrand",
            "username": "Tom",
            "email": "Tom@gmail.com",
            "phone": "00000002",
            "password": "12345Nano!",
            "confirm_password": "12345Nano!",
        }
    ]


#compte créer, puis connecter, puis accès à des infos protégées. 
@pytest.fixture
def subjects_fixture():
    return [{
            'title':'Crypto',
            'description' : "Ici nous parlons que de crypto",
            'keywords':'Crypto, Btc, Eth'
        },
        {
            'title':'Bourse',
            'description' : "Ici nous parlons que de Bourse",
            'keywords':'Bourse, Action, Etf, Obligation'
        },
        {
            'title':'Immo',
            'description' : "Ici nous parlons que d'immo",
            'keywords':'Appartement, prêt immo, maison, location'
        }
    ]

@pytest.fixture
def messages_fixture():
    return [{
            'text':'Salut la team !',
        },
        {
            'text':'Salut Hugo',
        },]

'''
        'Crypto1':{
            #on attent ici une erreur car le titre est similaire
            'title':'Crypto',
            'description' : 'Ici nous parlons que de crypto 1',
            'keywords':'Crypto1, Btc, Eth'
        }, 
        'Crypto2':{
            #on attent ici aucune erreur malgré une même description et les mêmes keywords
            'title':'Crypto',
            'description' : 'Ici nous parlons que de crypto',
            'keywords':'Crypto, Btc, Eth'
        }
    }
'''  

#enregistre tous les users
@pytest.fixture
def register_user(api_client, accounts_fixture):
    register_url = reverse('user-list')
    users = []
    for account_fixture in accounts_fixture:
        response = api_client.post(register_url, account_fixture, format='json')
        assert response.status_code == 201
        user = User.objects.get(username=account_fixture['username'])
        users.append(user)
    return users
#connect tous les users
@pytest.fixture
def user_token(api_client, accounts_fixture, register_user):
    token_url = reverse('token_obtain_pair')
    tokens = []
    for account_fixture in accounts_fixture:
        data = {
            'email': account_fixture['email'],
            'password': account_fixture['password']
        }
        response = api_client.post(token_url, data, format='json')
        assert response.status_code == 200
        tokens.append(response.data)
    return tokens
#Créer un sujet pour chaque user
@pytest.fixture
def create_subject(api_client, user_token, subjects_fixture):
    responses = []
    for i in range(3):
        access_token = user_token[i]['access']
        url = reverse('create_subject')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = api_client.post(url, subjects_fixture[i], format='json')
        responses.append(response)
    return responses

@pytest.mark.django_db
class TestSubjectAPI:
    '''Subject : 
    List : 
        - trier du plus au moins populaire
        - avoir tous les mots clés
        - récupérer un sujet par mot_clés
        - essayer de récupérer les sujets créer par l'user
    Detail : 
        - récupère le sujet 
    Post : 
        - essayer de créer un sujet 
    '''
    #Ici on vérifie que les sujets de base se créer correctement
    def test_create_subject(self, create_subject, register_user, subjects_fixture):
        # chaque user a créer un sujet via create_subject
        responses = create_subject
        i = 0
        for response in responses:
            #On initialise le sujet qui est traité et l'user 
            user = register_user[i]
            subject = subjects_fixture[i]
            #On vérifie la réponse retourné
            assert response.status_code == 201
            assert response.data['title'] == subject['title']
            #On vérifie que le sujet à bien été enregistré
            db_subject = Subject.objects.get(created_user = user)
            assert db_subject.title == subject['title']
            assert db_subject.description == subject['description']
            # Vérifie les mots-clés associés
            fixture_keywords = [word.strip().lower() for word in subject['keywords'].split(',')]
            for keyword in fixture_keywords:
                assert KeyWord.objects.filter(keyword=keyword, subject=db_subject).exists()
            i += 1
    #ici on vient vérifier que tous les sujets sont accessibles à tous les users
    def test_get_detail_subject(self, api_client, register_user, user_token, create_subject, subjects_fixture):
        users = register_user
        responses = create_subject
        tokens = user_token
        # boucle sur les users pour acceder à la page avec tous les users
        for i in range(3): 
            count = 0
            # boucle sur les sujets créer 
            for response in responses : 
                subject = Subject.objects.get(title=response.data['title'])
                #requete
                access_token = tokens[i]['access']
                url = reverse('subject-detail', kwargs={'pk': subject.id})
                api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
                response = api_client.get(url, format='json')
                #verif des réponse 'title','description','username'
                assert response.status_code == 200
                assert response.data['title'] == subjects_fixture[count]['title']
                assert response.data['description'] == subjects_fixture[count]['description']
                assert response.data['username'] == users[count].username
                count +=1

    def test_send_read_messages(self, api_client, register_user, user_token, create_subject, subjects_fixture, messages_fixture):
        users = register_user
        responses = create_subject
        tokens = user_token
        subject = subjects_fixture[1]
        subject = Subject.objects.get(title = subject['title'])
        #envoie des messages
        for i in range(3):
            url = reverse('subject-messages', kwargs={'subject_id': subject.id})
            api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens[i]['access'])
            if i < 2: 
                response = api_client.post(url, messages_fixture[i], format='json')
            else : 
                file = SimpleUploadedFile("test_file.txt", b"file_content", content_type="text/plain")
                data = {
                    'text':'Salut la team !',
                    'file':file
                }
                response = api_client.post(url, data, format='json')
            print(response)
            assert response.status_code == 201
        document = Message.objects.get(text='Salut la team !')
        assert document.file.name == f"documents/{file.name}"

'''
        # on vérifie que les mots clés ont bien été enregistrés 
        fixture_keywords = [word.strip().lower() for word in subject_fixture['keywords'].split(',')]
        for keyword in fixture_keywords:
            assert keyword in response.data['keywords']
'''


'''
    # Créer un fichier temporaire
    file = SimpleUploadedFile("test_file.txt", b"file_content", content_type="text/plain")
    
    # Créer les données de requête
    data = {
        "title": "Test Document",
        "file": file
    }
    
    # Faire une requête POST pour créer un nouveau document
    url = reverse('document-list')  # Assure-toi que cette URL est correcte pour ton cas
    response = api_client.post(url, data, format='multipart')
    
    # Vérifier que la requête a réussi
    assert response.status_code == 201
    
    # Vérifier que le document a bien été créé
    from .models import Document
    document = Document.objects.get(title="Test Document")
    assert document.file.name == f"documents/{file.name}"
    '''
    

'''
    def test_get_list_subject(self, api_client, register_user, user_token, create_subject, subjects_fixture):

        Ici je dois récupèrer : 
        - titre 
        - user qui l'a créer 
        - l'activité hebdomadaire 
        - les keywords 

'''

    




        


