from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import User, Setting

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
    
class SettingSerializer(ModelSerializer): 
    class Meta: 
        model=Setting
        fields='__all__'

    def validate(self,data): 
        if data['currency'] not in Setting.CurrencyList: 
            raise serializers.ValidationError('You must choose between Euro and Dollar.')
        if data['color'] not in Setting.Colors:
            raise serializers.ValidationError('You must choose between Gray/Red/Pink/Purple/Blue/Green/Brown/Yellow')
        return data

# deux autres choses à gérer : * verif user dans modif via clé OTP. 
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    setting = SettingSerializer(many=False, read_only=True)

    class Meta: 
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone', 'country', 'job', 'income', 'birthday',
            'setting', 'password', 'confirm_password'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        user = self.instance
        if User.objects.filter(username=data['username']).exclude(id=user.id if user else None).exists():
            raise serializers.ValidationError('Username already exists.')
        if User.objects.filter(phone=data['phone']).exclude(id=user.id if user else None).exists():
            raise serializers.ValidationError('Phone number already exists.')
        if User.objects.filter(email=data['email']).exclude(id=user.id if user else None).exists(): 
            raise serializers.ValidationError('E-Mail already exists.')
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        if not instance.OTP_Status():
            raise serializers.ValidationError("La vérification OTP n'a pas été effectuée")
        
        validated_data.pop('confirm_password', None)
        
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        return super().update(instance, validated_data)

