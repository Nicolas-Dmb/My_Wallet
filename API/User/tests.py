import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
# models.py
'''
- Tester de créer un user avec et sans les blank True
- Tester de créer un user avec deux fois la même Username/Email/Phone
- Configurer les settings en faisant une erreur dans CurrencyList
- Configurer les settings en faisant une erreur dans Colors 
- Configurer normalement le setting 
- Se connecter 
- refresh 
- on véirife que les OTP Set et OTP Status fonctionne bien. 
'''
#serializers.py
'''
Test : 
- envoyer setting avec autre que currency et color
- envoyer avec des données valides
User :
- créer un compte puis le modifier
- créer et modifier un compte avec un nom / un tel / un mail déjà enregistré
- modifier un compte sans avoir de validation OTP
- tester un get sur une liste User et une liste Setting
'''
#views.py
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

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

#compte créer, puis connecter, puis accès à des infos protégées. 
@pytest.fixture(params=['less_informations','all_informations'])
def account_fixture(request):
    data = {
        'less_informations':{
            "first_name": "Py",
            "last_name": "Test",
            "username": "PyTest",
            "email": "nicolas.dambreville@epitech.eu",
            "phone": "00000000",
            "password": "12345Nano!",
            "confirm_password": "12345Nano!"
        },
        'all_informations':{
            "first_name": "PyAll",
            "last_name": "TestAll",
            "username": "PyTestAll",
            "email": "nicolas.all@epitech.eu",
            "phone": "11111111",
            "country": "france",
            "job": "student",
            "income": "0",
            "birthday":"2000-12-20",
            "password": "12345Nano!",
            "confirm_password": "12345Nano!"
        },
    }
    return data[request.param]

@pytest.fixture
def register_user(api_client, account_fixture):
    register_url = reverse('user-list')
    response = api_client.post(register_url, account_fixture, format='json')
    assert response.status_code == 201
    user = User.objects.get(username=account_fixture['username'])
    return user

@pytest.fixture
def user_token(api_client, account_fixture):
    token_url = reverse('token_obtain_pair')
    data = {
        'username': account_fixture['username'],
        'password': account_fixture['password']
    }
    response = api_client.post(token_url, data, format='json')
    assert response.status_code == 200
    return response.data

@pytest.mark.django_db
class TestUserAPI:

    def test_user_registration(self, api_client, account_fixture):
        register_url = reverse('user-list')
        response = api_client.post(register_url, account_fixture, format='json')
        if response.status_code != 201: 
            print(response)
        assert response.status_code == 201
        assert User.objects.count() == 1
        user = User.objects.get(username=account_fixture['username'])
        assert user.username == account_fixture['username']

    def test_user_login(self, api_client, register_user, account_fixture):
        token_url = reverse('token_obtain_pair')
        data = {
            'username': account_fixture['username'],
            'password': account_fixture['password']
        }
        response = api_client.post(token_url, data, format='json')
        if response.status_code != 200: 
            print(response)
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_access_protected_route(self, api_client, register_user, user_token):
        access_token = user_token['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        detail_url = reverse('user-detail', kwargs={'pk': register_user.pk})
        response = api_client.get(detail_url)

        if response.status_code != 200: 
            print(response)
        assert response.status_code == 200
        user_data = response.data
        assert user_data['username'] == register_user.username
        assert user_data['email'] == register_user.email
        assert user_data['first_name'] == register_user.first_name
        assert user_data['last_name'] == register_user.last_name
        assert user_data['phone'] == register_user.phone

    def test_only_one_user(self, api_client, account_fixture):
        #On engegistre les deux users : 
        register_url = reverse('user-list')
        for account in account_fixture.values(): 
            response = api_client.post(register_url, account_fixture[account], format='json')
            print (response.data)
            assert response.status_code == 201
        #on se connect avec l'un puis l'autre
        token_url = reverse('token_obtain_pair')
        for account in account_fixture.values():
            data = {
                'username': account['username'],
                'password': account['password']
                }
            response = api_client.post(token_url, data, format='json')
            assert response.status_code == 200
            access_token = response.data['access']
             # on regarde si la requete renvoie que un ou deux users
            api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
            listuser = reverse('user-list')
            response = api_client.get(listuser)

            assert response.status_code == 200
            user_data = response.data
            assert user_data['username'] == account['username']
            assert user_data['email'] == account['email']
            assert user_data['first_name'] == account['first_name']
            assert user_data['last_name'] == account['last_name']
            assert user_data['phone'] == account['phone']


#Création de compte invalides + test_only_one_user que je vais intégrer ici en enregistrant les deux users de base qui sont corrects. 
@pytest.fixture
def failes_user():
    return {
        'less_informations':{
            "first_name": "Py",
            "last_name": "Test",
            "username": "PyTest",
            "email": "nicolas.dambreville@epitech.eu",
            "phone": "00000000",
            "password": "12345Nano!",
            "confirm_password": "12345Nano!"
        },#enregistrement valide 
        'all_informations':{
            "first_name": "PyAll",
            "last_name": "TestAll",
            "username": "PyTestAll",
            "email": "nicolas.all@epitech.eu",
            "phone": "11111111",
            "country": "france",
            "job": "student",
            "income": "0",
            "birthday":"2000-12-20",
            "password": "12345Nano!",
            "confirm_password": "12345Nano!"
        },#enregistrement valide 
        'same_first_name':{
            "first_name": "Py",
            "last_name": "Test1",
            "username": "PyTest1",
            "email": "n@epitech.eu",
            "phone": "00000001",
            "password": "12345Nano!",
            "confirm_password": "12345Nano!"
        },#Erreur first_name similaire 
        'same_last_name':{
            "first_name": "Py1",
            "last_name": "Test",
            "username": "PyTest1",
            "email": "n@epitech.eu",
            "phone": "00000001",
            "password": "12345Nano!",
            "confirm_password": "12345Nano!"
        },#Erreur lastName similaire 
        'same_username':{
            "first_name": "Py1",
            "last_name": "Test1",
            "username": "PyTest",
            "email": "n@epitech.eu",
            "phone": "00000001",
            "password": "12345Nano!",
            "confirm_password": "12345Nano!"
        }, #Erreur Username Similaire 
        'same_email':{
            "first_name": "Py1",
            "last_name": "Test1",
            "username": "PyTest1",
            "email": "nicolas.dambreville@epitech.eu",
            "phone": "00000001",
            "password": "12345Nano!",
            "confirm_password": "12345Nano!"
        },#erreur email similaire 
        'same_phone':{
            "first_name": "Py1",
            "last_name": "Test1",
            "username": "PyTest1",
            "email": "n@epitech.eu",
            "phone": "00000000",
            "password": "12345Nano!",
            "confirm_password": "12345Nano!"
        },#erreur tel similaire 
        'incorrect_confirm_password':{
            "first_name": "Py1",
            "last_name": "Test1",
            "username": "PyTest1",
            "email": "n@epitech.eu",
            "phone": "00000001",
            "password": "12345Nano!",
            "confirm_password": "12345Nano"
        },#erreur confirm password incorrect 
        'unsafe_password_1':{
            "first_name": "Py1",
            "last_name": "Test1",
            "username": "PyTest1",
            "email": "n@epitech.eu",
            "phone": "00000001",
            "password": "1234",
            "confirm_password": "12345"
        },#erreur password insécurisé
        'unsafe_password_2':{
            "first_name": "Py1",
            "last_name": "Test1",
            "username": "PyTest1",
            "email": "n@epitech.eu",
            "phone": "00000001",
            "password": "12345Nano!",
            "confirm_password": "12345Nano"
        },#erreur password insécurisé
    }
