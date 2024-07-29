import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from django.test import TestCase



# models.py
'''
- Configurer les settings en faisant une erreur dans CurrencyList
- Configurer les settings en faisant une erreur dans Colors 
- Configurer normalement le setting 
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

class TestEmailSending(TestCase):
    def test_email_sent(self):
        # Simuler un envoi d'email
        mail.send_mail(
            'Subject here',
            'Here is the message.',
            'from@example.com',
            ['to@example.com'],
            fail_silently=False,
        )

        # Vérifier que l'email a été envoyé
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Subject here')
        self.assertEqual(email.body, 'Here is the message.')
        self.assertEqual(email.from_email, 'from@example.com')
        self.assertEqual(email.to, ['to@example.com'])



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
            "email": "bklbjk@gmail.com",
            "phone": "00000000",
            "password": "12345Nano!",
            "confirm_password": "12345Nano!"
        },
        'all_informations':{
            "first_name": "PyAll",
            "last_name": "TestAll",
            "username": "PyTestAll",
            "email": "n.all@epitech.eu",
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

@pytest.fixture
def get_otp(api_client, register_user, user_token):
    user = register_user
    access_token = user_token["access"]

    #on demande la génération d'un code OTP
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    url = reverse('OTP')
    response = api_client.get(url)
    assert response.status_code == 201 or response.status_code == 200

    if response.status_code == 200 : 
        return True # pas besoin de post OTP
    else : 
        return False # besoin de post OTP
    
@pytest.fixture
def post_otp(api_client, account_fixture, get_otp, user_token):
    if get_otp == True : 
        return True
    user = User.objects.get(username=account_fixture['username'])
    access_token = user_token["access"]
    otp_key = user.otp_key
    payload = {'otp':otp_key}
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
    url = reverse('OTP')
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 200
    return True    

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

    def test_refresh_token(self, api_client, register_user, user_token):
        old_access_token = user_token['access']
        refresh_token = user_token['refresh']

        payload = {'refresh': refresh_token}
        url = reverse('token_refresh')
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 200
        data = response.data
        access_token = data['access']

        assert access_token != old_access_token


@pytest.mark.django_db
class TestOTPAPI:
    def test_success_OTP(self, api_client, register_user, user_token): 
        user = register_user
        access_token = user_token['access']

        # Get sur OTPAPIView
        url = reverse('OTP')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = api_client.get(url)
        assert response.status_code == 201

        # On vérifie que l'email est envoyé
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.subject == 'Votre code OTP'
        assert email.to == [user.email]
        
        # Extrait le code OTP du corps de l'email
        otp_code = int(email.body.split(': ')[1].strip())

        # On vérifie que le code généré est valide et que le code stocké dans la db est aussi le même
        user = User.objects.get(username=user.username)
        assert user.otp_key == int(otp_code)
        last_otp_generate = user.otp_generate + timezone.timedelta(seconds=60)
        assert last_otp_generate > timezone.now()

        # On simule l'appel 
        payload = {'otp': otp_code}
        response = api_client.post(url,payload,format='json')
        print(f'Response: {response.content}')
        assert response.status_code == 200

        # Vérifier que l'utilisateur est vérifié et que son email est vérifié aussi 
        user = User.objects.get(username=user.username)
        valid_otp = user.otp_verif
        assert valid_otp > timezone.now()
        assert user.email_verif is True
        assert user.OTP_Status() is True
        assert user.otp_key is None

    
    def test_already_valid_otp(self, api_client, register_user, user_token, post_otp, get_otp): 
        #on verifie que l'user peux changer les infos de son compte sans taper l'otp

        # On fait les vérifs de post_otp
        retour = post_otp
        assert retour == True
        # On modifie les infos de l'user
        url = reverse('user-detail', kwargs={'pk': register_user.pk})
        access_token = user_token['access']
        data = {
            "username": "PyTe",
            "email": "bkjk@gmail.com",
            "phone": "007800000",
        }
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = api_client.patch(url, data, format='json')
        print(response.content)
        assert response.status_code == 200
        assert User.objects.filter(username = "PyTe").exists()
        user = User.objects.get(username = "PyTe")
        assert user.username == "PyTe"
        assert user.email == "bkjk@gmail.com"
        assert user.phone == "007800000"


        
'''
    def timeout_otp(self, api_client, register_user, user_token): 
        # on verifie le retour puis si un seconde code otp est envoyé et que l'user le saisie correctement. 

    def wrong_otp_key(self, api_client, register_user, user_token):
        #l'user tape un mauvais code otp puis saisie le bon otp 

    def not_necessary_otp_key(self, api_client, register_user, user_token):
        # l'user demande une clé otp alors que son code est déjà valide 
'''


#Création de compte invalides + test_only_one_user que je vais intégrer ici en enregistrant les deux users de base qui sont corrects. 
@pytest.fixture
def failes_user():
    return {
        'less_informations':{
            "first_name": "Py",
            "last_name": "Test",
            "username": "PyTest",
            "email": "dzejkbekj@gmail.com",
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
            "email": "dzejkbekj@gmail.com",
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



@pytest.mark.django_db
class TestfailUserAPI:
    def test_user_registration(self, api_client, failes_user):
        register_url = reverse('user-list')
        for key, user_data in failes_user.items():
            response = api_client.post(register_url, user_data, format='json')
            if key in ["less_informations","all_informations"]:
                assert response.status_code == 201
                user = User.objects.get(username=user_data['username'])
                assert user.username == user_data['username']
            else : 
                print(key)
                print(response)
                assert response.status_code == 400

    # on s'assure ici que l'user ne peut accéder qu'à ses informations et non à tous les users. 
    def test_only_one_user(self, api_client, failes_user):
        #On engegistre les deux users : 
        accounts = ["less_informations","all_informations"]
        register_url = reverse('user-list')
        for account in accounts: 
            response = api_client.post(register_url, failes_user[account], format='json')
            print (response.data)
            assert response.status_code == 201
        #on se connect avec l'un puis l'autre
        token_url = reverse('token_obtain_pair')
        for account in accounts:
            data = {
                'username': failes_user[account]['username'],
                'password': failes_user[account]['password']
                }
            response = api_client.post(token_url, data, format='json')
            assert response.status_code == 200
            access_token = response.data['access']
                # on regarde si la requete renvoie que un ou deux users
            api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
            listuser = reverse('user-list')
            response = api_client.get(listuser)

            assert response.status_code == 200

            user_data_list = response.data
            assert len(user_data_list) == 1
            user_data = user_data_list[0]
            
            assert user_data['username'] == failes_user[account]['username']
            assert user_data['email'] == failes_user[account]['email']
            assert user_data['first_name'] == failes_user[account]['first_name']
            assert user_data['last_name'] == failes_user[account]['last_name']
            assert user_data['phone'] == failes_user[account]['phone']
