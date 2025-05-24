from django.urls import path, re_path
from web import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('login/', views.login, name='login'),

]
