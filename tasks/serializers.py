from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Tasks


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150,required=True)
    password = serializers.CharField(write_only=True,validators = [validate_password],required=True)

    class Meta:
        model = User
        fields = ['username','password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
    

class TaskSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username',read_only=True)
    class Meta:
        model = Tasks
        fields = ['id', 'title', 'desc', 'username', 'created_at',"status","priority"]
        read_only_fields = ['created_at','username']