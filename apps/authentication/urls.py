from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # We'll add the actual views later, for now just empty patterns
    # path('login/', views.LoginView.as_view(), name='login'),
    # path('logout/', views.LogoutView.as_view(), name='logout'),
]
