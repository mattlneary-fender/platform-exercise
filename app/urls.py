from django.urls import path, re_path

from apps.users.views import (LoginView,
                              LogOutView,
                              UserRegistrationView,
                              UserView,)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogOutView.as_view(), name='logout'),
    path('users/', UserView.as_view(), name='users-api'),
]
