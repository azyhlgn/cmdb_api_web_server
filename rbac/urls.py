from django.urls import path
from rbac import views as rbac_views

urlpatterns = [
    path('permission_multi/', rbac_views.permission_multi, name='permission_multi'),
    path('permission_distribution/', rbac_views.permission_distribution, name='permission_distribution'),
]
