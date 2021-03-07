from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView

from django.contrib.auth import authenticate

from .models import User
from .serializers import LoginUserSerializer


class BearerTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'


class UserRegistrationView(APIView):
    serializer_class = LoginUserSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        email = request.data.get('email')
        if User.objects.filter(email=email).count():
            return Response('A user with that email already exists, please login', status=status.HTTP_400_BAD_REQUEST)

        name = request.data.get('name')
        password = request.data.get('password')

        new_user = User.objects.create(email=email, name=name)
        new_user.set_password(password)
        new_user.save()

        authenticate(username=new_user.email, password=new_user.password)

        token = Token.objects.create(user=new_user)

        return Response({
            'token': token.key,
            'user_id': new_user.id,
            'email': new_user.email
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    serializer_class = LoginUserSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        email = request.data.get('email')
        password = request.data.get('password')

        if not authenticate(username=email, password=password):
            return Response('Invalid credentials', status=status.HTTP_403_FORBIDDEN)

        user = User.objects.get(email=email)

        if user.auth_token:
            user.auth_token.delete()

        new_token = Token.objects.create(user=user)

        return Response({
            'token': new_token.key,
            'user_id': user.id,
            'email': user.email
        }, status=status.HTTP_200_OK)


class LogOutView(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response()


class UserView(APIView):
    serializer_class = LoginUserSerializer
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        return Response({
            'user_id': user.id,
            'email': user.email,
            'name': user.name
        }, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user

        new_email = serializer.data['email']
        if user.email != serializer.data['email'] and User.objects.filter(email=new_email).count():
            return Response('Email already in use.', status=status.HTTP_400_BAD_REQUEST)
        user.email = new_email
        user.name = serializer.data['name']

        password_changed = False
        request_password = serializer.data['password']
        if not user.check_password(request_password):
            user.set_password(request_password)
            password_changed = True
        user.save()

        return Response({
            'user_id': user.id,
            'email': user.email,
            'name': user.name,
            'password_changed': password_changed
        }, status=status.HTTP_200_OK)
