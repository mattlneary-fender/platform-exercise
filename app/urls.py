from django.urls import path, re_path

from apps.users.views import (LoginView,
                              LogOutView,
                              UserRegistrationView,
                              UserView,)

urlpatterns = [
    path('register/', UserRegistrationView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogOutView.as_view()),
    path('users/', UserView.as_view()),
]
