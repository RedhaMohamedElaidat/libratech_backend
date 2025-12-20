from rest_framework import serializers  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer  # type: ignore

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour afficher les données utilisateur"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'address', 'role', 'joined_date')
        read_only_fields = ('id', 'joined_date')


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription de nouveaux utilisateurs"""
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)
    full_name = serializers.CharField(source='first_name', required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'full_name', 'phone', 'address')
    
    def validate(self, data):
        """Valider que les mots de passe correspondent"""
        password = data.get('password')
        password_confirm = self.initial_data.get('password_confirm')
        
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'Les mots de passe ne correspondent pas.'
            })
        
        # Vérifier si l'email existe déjà
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({
                'email': 'Cet email est déjà utilisé.'
            })
        
        # Vérifier si le username existe déjà
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({
                'username': 'Ce nom d\'utilisateur est déjà utilisé.'
            })
        
        return data
    
    def create(self, validated_data):
        """Créer un nouvel utilisateur"""
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            **validated_data,
            password=password
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer pour la connexion"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        """Valider les credentials"""
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            raise serializers.ValidationError({
                'error': 'Le nom d\'utilisateur et le mot de passe sont obligatoires.'
            })
        
        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'  # <-- Ajouter cette ligne pour login par email

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Ajouter des champs personnalisés au token
        token['username'] = user.username
        token['email'] = user.email
        token['full_name'] = user.get_full_name()
        token['user_id'] = user.id
        token['role'] = getattr(user, 'role', 'user')
        
        return token



class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour changer le mot de passe"""
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, min_length=6, required=True)
    new_password_confirm = serializers.CharField(write_only=True, min_length=6, required=True)
    
    def validate(self, data):
        """Valider les mots de passe"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Les nouveaux mots de passe ne correspondent pas.'
            })
        
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({
                'new_password': 'Le nouveau mot de passe doit être différent de l\'ancien.'
            })
        
        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour mettre à jour le profil utilisateur"""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone', 'address', 'email')
        
    def validate_email(self, value):
        """Vérifier que l'email n'est pas déjà utilisé"""
        user = self.context.get('request').user
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError('Cet email est déjà utilisé.')
        return value
