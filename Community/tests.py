import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from Community.models import Subject, Favori, Message, KeyWord
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
import os

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

@pytest.fixture
def send_messages(api_client, user_token, create_subject, subjects_fixture):
    tokens = user_token
    subject = subjects_fixture[1]
    subject = Subject.objects.get(title = subject['title'])
    data = {
                'text':'Salut !',
    }
    #envoie des messages
    for y in range(4): #pour envoyer 4(y) fois  avec les 3(i) users
        for i in range(3):
            url = reverse('send_message', kwargs={'subject_id': subject.id})
            api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens[i]['access'])
            response = api_client.post(url, data, format='json')
            assert response.status_code == 201
    
    return subject

@pytest.fixture
def send_messages_all_subject(api_client, user_token, create_subject, subjects_fixture):
    tokens = user_token    
    data = {
                'text':'Salut !',
    }
    order = []
    #envoie des messages dans le sujet 1
    for y in range(4): #pour envoyer 4(y) fois  avec les 3(i) users
        for i in range(3):
            subject = Subject.objects.get(title = subjects_fixture[1]['title'])
            url = reverse('send_message', kwargs={'subject_id': subject.id})
            api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens[i]['access'])
            response = api_client.post(url, data, format='json')
            assert response.status_code == 201
    order.append(subject.title)
    #envoie d'un message dans le sujet 2
    subject = Subject.objects.get(title = subjects_fixture[2]['title'])
    order.append(subject.title)
    url = reverse('send_message', kwargs={'subject_id': subject.id})
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens[i]['access'])
    response = api_client.post(url, data, format='json')
    assert response.status_code == 201

    subject = Subject.objects.get(title = subjects_fixture[0]['title'])
    order.append(subject.title)
    
    return order

@pytest.mark.django_db
class TestSubjectAPI:
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

    def test_get_list_subject(self, api_client, register_user, user_token, create_subject, subjects_fixture):
        url = reverse('subject-list')
        users = register_user
        subjects = create_subject
        tokens = user_token
        for token in tokens:
            #requete
            access_token = token['access']
            api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
            response = api_client.get(url, format='json')
            #verif des réponse 'title','weekly_activity','username'
            assert response.status_code == 200
            assert len(response.data) == 3
            for i in range(3): 
                response_subject = response.data[i]['subject']
                subject = Subject.objects.get(title=response_subject['title'])
                assert response_subject['title'] == subjects_fixture[i]['title']
                assert response_subject['weekly_activity'] == subject.know_subject_activity()
                assert response_subject['username'] == users[i].username
                # on vérifie que les mots clés ont bien été enregistrés 
                response_keywords = response.data[i]['keywords']
                fixture_keywords = [word.strip().lower() for word in subjects_fixture[i]['keywords'].split(',')]
                for keyword in fixture_keywords:
                    assert keyword in response_keywords
        
    def test_get_weekly_activity(self, api_client, register_user, user_token, send_messages):
        subject =  send_messages
        users = register_user
        tokens = user_token
        # on requete la liste de sujet 
        def getsubjectlist(): 
            url = reverse('subject-list')
            api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens[1]['access'])
            responses = api_client.get(url, format='json')
            assert responses.status_code == 200
            for response in responses.data:
                response = response['subject']
                if response['title'] == subject.title: # on verifie que le sujet est bien le même 
                    response_subject = response
            return response_subject
        # on vérifie que l'activité du sujet est bien 
        response = getsubjectlist()
        assert response['weekly_activity'] == 12
        # on va modifié le week dans subject pour initialisé les messages
        subject = Subject.objects.get(title=subject.title)
        subject.week = subject.week-1
        subject.save()
        # on refait la requete 
        response = getsubjectlist()
        assert response['weekly_activity'] == 0
        # on renvoie des messages
        data = {'text':'Salut !'}
        url = reverse('send_message', kwargs={'subject_id': subject.id})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens[1]['access'])
        response = api_client.post(url, data, format='json')
        assert response.status_code == 201
        response = getsubjectlist()
        assert response['weekly_activity'] == 1

    def test_get_own_subjects(self, api_client, register_user, accounts_fixture, subjects_fixture):
        account = accounts_fixture[0]
        #on récupère le token 
        token_url = reverse('token_obtain_pair')
        data = {
            'email': account['email'],
            'password': account['password'],
        }
        response = api_client.post(token_url, data, format='json')
        assert response.status_code == 200
        token = response.data
        #On créer les sujets pour un user
        for i in range(3):
            url = reverse('create_subject')
            api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token['access'])
            response = api_client.post(url, subjects_fixture[i], format='json')
            print(response.data)
            assert response.status_code == 201
        #on requete les sujets de l'user
        url = reverse('own-subjects')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token['access'])
        response = api_client.get(url, format='json')
        assert response.status_code == 200
        assert len(response.data)==3
        for subject in response.data:
            assert subject['username'] == account['username']

    #on vérifie que la liste sort dans l'ordre du plus populaire au moins populaire
    def test_order_list_subject(self, api_client,user_token, send_messages_all_subject):
        tokens = user_token
        order = send_messages_all_subject
        url = reverse('subject-list')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens[1]['access'])
        response = api_client.get(url, format='json')
        assert response.status_code == 200
        for i in range(3):
            data = response.data[i]
            assert order[i] == data['subject']['title']


@pytest.mark.django_db
class TestMessagesAPI:
    def test_send_read_messages(self, api_client, register_user, user_token, create_subject, subjects_fixture, messages_fixture):
        users = register_user
        responses = create_subject
        tokens = user_token
        subject = subjects_fixture[1]
        subject = Subject.objects.get(title = subject['title'])
        #envoie des messages
        for i in range(3):
            url = reverse('send_message', kwargs={'subject_id': subject.id})
            api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens[i]['access'])
            if i < 2 : 
                response = api_client.post(url, messages_fixture[i], format='json')
            else : 
                file = SimpleUploadedFile("test_file.txt", b"file_content", content_type="text/plain")
                data = {
                    'text':'Salut !',
                    'file':file
                }
                response = api_client.post(url, data, format='multipart')
            assert response.status_code == 201
        message = Message.objects.get(text='Salut !')
        user = users[2]
        assert message.file.name == f"{subject.id}_{user.id}_{message.date.strftime('%Y-%m-%d-%H-%M-%S')}_{file.name}"
        if os.path.exists(message.file.path):
            os.remove(message.file.path)

        #voir les messages pour tous les users 
        for i in range(3):
            url = reverse('subject-messages', kwargs={'subject_id': subject.id})
            api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens[i]['access'])
            response = api_client.get(url, format='json')
            assert response.status_code == 200
            print(response.data)
            data = response.data
            assert data['count'] == 3
            messages = data['results']
            expected_messages = [{
                'text':'Salut !',
                'username':'Tom',
            },{
                'text':'Salut Hugo',
                'username':'Marie',
            },{
                'text':'Salut la team !',
                'username':'Hugo',
            }]
            for i, message in enumerate(messages): 
                assert message['text'] == expected_messages[i]['text']
                assert message['username'] == expected_messages[i]['username']
                if message['text'] == 'Salut !':
                    assert message['file'] is not None
                else : 
                    assert message['file'] is None

    def test_pagination_messages(self, api_client, register_user, user_token, create_subject, subjects_fixture):
        tokens = user_token
        subject = subjects_fixture[2]
        subject = Subject.objects.get(title = subject['title'])
        data = {
                    'text':'Salut !',
        }
        #envoie des messages
        for y in range(4):
            for i in range(3):
                url = reverse('send_message', kwargs={'subject_id': subject.id})
                api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens[i]['access'])
                response = api_client.post(url, data, format='json')
                assert response.status_code == 201

        #vérifier que la pagination est bien présente. 
        url = reverse('subject-messages', kwargs={'subject_id': subject.id})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens[1]['access'])
        response = api_client.get(url, format='json')
        assert response.status_code == 200
        data = response.data
        assert data['count'] == 12
        assert len(data['results']) == 10

        # acceder à la pagination 'next'
        url_next = data['next']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens[1]['access'])
        response = api_client.get(url_next, format='json')
        assert response.status_code == 200
        data = response.data
        assert data['count'] == 12
        assert len(data['results']) == 2

        #acceder à la pagination 'previous'
        url_previous = data['previous']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens[1]['access'])
        response = api_client.get(url_previous, format='json')
        assert response.status_code == 200
        data = response.data
        assert data['count'] == 12
        assert len(data['results']) == 10

@pytest.mark.django_db
class TestFavorisAPI:
    def test_send_and_receive_Favoris(self, api_client, register_user, user_token, create_subject, subjects_fixture):
        token = user_token[1]
        subject_1 = Subject.objects.get(title = subjects_fixture[1]['title'])
        subject_0 = Subject.objects.get(title = subjects_fixture[0]['title'])
        #on envoie un sujet en favori
        url = reverse('favoris_community')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token['access'])
        response = api_client.post(url, {"subject": subject_1.id}, format='json')
        assert response.status_code == 201
        #puis un deuxième sujet 
        response = api_client.post(url, {"subject": subject_0.id}, format='json')
        assert response.status_code == 201
        #puis on récupère les sujets favoris
        response = api_client.get(url, format='json')
        assert response.status_code == 200
        assert len(response.data) == 2
        print(response.data)
        subject_fav_1 = Subject.objects.get(id = response.data[1]['subject'])
        subject_fav_2 = Subject.objects.get(id = response.data[0]['subject'])
        assert subject_fav_1.title != subject_0.title
        assert subject_fav_2.title != subject_1.title
        assert subject_fav_1.title == subject_1.title
        assert subject_fav_2.title == subject_0.title
