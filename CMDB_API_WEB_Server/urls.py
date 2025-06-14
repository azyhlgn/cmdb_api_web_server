"""
URL configuration for CMDB_API_WEB_Server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from stark.service import stark

urlpatterns = [
    path('admin/', admin.site.urls),
    path('stark/', stark.site.urls),


    path('api/', include(('api.urls', 'api'), namespace='api')),
    path('rbac/', include(('rbac.urls', 'rbac'), namespace='rbac')),
    path('web/', include(('web.urls', 'web'), namespace='web')),
]
