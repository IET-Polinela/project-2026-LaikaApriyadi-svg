from django.urls import path
from .views import SignUpView, MyLogoutView, MyLoginView

urlpatterns = [
    path('login/', MyLoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
]