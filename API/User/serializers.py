from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import User, Setting
    
class SettingSerializer(ModelSerializer): 
    class Meta: 
        model=Setting
        fields = ['currency', 'nightMode', 'color', 'user']

    def validate(self, data): 
        if data['currency'] not in dict(Setting.CurrencyList.choices):
            raise serializers.ValidationError({
                'currency': 'You must choose between Euro and Dollar.'
            })
        if data['color'] not in dict(Setting.Colors.choices):
            raise serializers.ValidationError({
                'color': 'You must choose between Gray, Red, Pink, Purple, Blue, Green, Brown, Yellow.'
            })
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
        if 'username' in data and User.objects.filter(username=data['username']).exclude(id=user.id if user else None).exists():
            raise serializers.ValidationError('Username already exists.')
        if 'phone' in data and User.objects.filter(phone=data['phone']).exclude(id=user.id if user else None).exists():
            raise serializers.ValidationError('Phone number already exists.')
        if 'email' in data and User.objects.filter(email=data['email']).exclude(id=user.id if user else None).exists():
            raise serializers.ValidationError('E-Mail already exists.')

        if 'password' in data and 'confirm_password' in data:
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError('Passwords do not match.')

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

