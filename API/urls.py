from django.urls import path
from API import views as api_views



urlpatterns = [
    path('asset/', api_views.Asset.as_view(), name='asset'),
]
