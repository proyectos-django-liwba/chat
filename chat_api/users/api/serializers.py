from rest_framework import serializers
from users.models import User

# Serializador para registro de usuarios
class UserRegisterSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    class Meta:
        model = User
        fields = [ 'email','avatar', 'username','password','first_name', 'last_name', 'role']
   
    def create(self, validated_data):
      # encriptar el password
      password = validated_data.pop('password', None)
      instance = self.Meta.model(**validated_data)
      # si el password no es nulo
      if password is not None:
        instance.set_password(password)
        # guardar el usuario
        instance.save()
      return instance


# Serializador para el modelo User, autenticación de usuarios
class UserSerializer(serializers.ModelSerializer):
  class Meta:
      model = User
      fields = ['id', 'avatar', 'email','username', 'first_name', 'last_name', 'role']


# Serializador para el modelo User, actualización de usuarios
class UserUpdateSerializer(serializers.ModelSerializer):
  class Meta:
      model = User
      fields = ['email','avatar', 'username','first_name', 'last_name']

class UserUpdatePathSerializer(serializers.ModelSerializer):
  class Meta:
      model = User
      fields = ['id', 'avatar', 'email','username', 'first_name', 'last_name', 'role']
        
# Serializador para actualizar solo la contraseña
class UserChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['old_password', 'new_password']

    def update(self, instance, validated_data):
        old_password = validated_data.get('old_password')
        new_password = validated_data.get('new_password')

        if not instance.check_password(old_password):
            raise serializers.ValidationError({'old_password': 'Contraseña actual incorrecta.'})

        instance.set_password(new_password)
        instance.save()

        return instance

class VerificarCuentaSerializer(serializers.Serializer):
    
    otp = serializers.CharField()
    class Meta:
      model = User
      fields = ['id', 'avatar', 'email','username', 'first_name', 'last_name', 'role', 'otp', 'is_verified']


class UserSerializerUsername(serializers.ModelSerializer):
  class Meta:
      model = User
      fields = ['id', 'avatar', 'username','role']


class UserChangePasswordRecoverSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    otp = serializers.CharField()
    class Meta:
        model = User
        fields = ['password', 'confirm_password', 'otp']

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        confirm_password = validated_data.get('confirm_password')
        

        if password != confirm_password:
            raise serializers.ValidationError({'password': 'Las contraseñas no coinciden.'})

        instance.set_password(password)
        instance.save()

        return instance