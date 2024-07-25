import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()
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

@pytest.fixture
def account_fixture():
    data = {        
        "first_name": "Py",
        "last_name": "Test",
        "username": "PyTest",
        "email": "nicolas.dambreville@epitech.eu",
        "phone": "00000000",
        "country": "",
        "job": "",
        "income": "",
        "birthday": "",
        "password": "12345Nano!",
        "confirm_password": "12345Nano!"}
    return data

@pytest.fixture
def setting_fixture():
    data = {"currency":"Dollar", "nightMode":"False", "color":"Blue"}
    return data

@pytest.fixture
def api_client():
    return APIClient()
#Pour créer une base de données temporaire (à intégrer à chaque test)
@pytest.mark.django_db
class TestUserAPI:

    def test_user_registration(self, api_client, account_fixture):
        register_url = reverse('user')
        response = api_client.post(register_url, account_fixture, format='json')
        assert response.status_code == 201
        assert User.objects.count() == 1
        assert User.objects.get().username == 'PyTest'

    def test_user_login(self, api_client, account_fixture):
        register_url = reverse('user')
        api_client.post(register_url, account_fixture, format='json')
        
        token_url = reverse('api/token/')
        data = {
            'username': 'PyTest',
            'password': 'Testpassword123'
        }
        response = api_client.post(token_url, data, format='json')
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_access_protected_route(self, api_client, account_fixture):
        register_url = reverse('user')
        api_client.post(register_url, account_fixture, format='json')
        
        token_url = reverse('api/token/')
        data = {
            'username': 'PyTest',
            'password': 'Testpassword123'
        }
        token_response = api_client.post(token_url, data, format='json')
        access_token = token_response.data['access']
        
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = api_client.get(reverse('user'))
        user_data = response.data
        assert user_data['username'] == 'PyTest'
        assert user_data['email'] == 'nicolas.dambreville@epitech.eu'
        assert user_data['first_name'] == 'Py'
        assert user_data['last_name'] == 'Test'
        assert user_data['phone'] == '00000000'
        assert response.status_code == 200

