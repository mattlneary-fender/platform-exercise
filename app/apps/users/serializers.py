from rest_framework import serializers


class LoginUserSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False)
    email = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(max_length=100,required=True)
