from django.urls import path, re_path
from WEB import views

urlpatterns = [
    path('index/', views.index, name='index'),

    path('businessunit/', views.businessunit_list, name='businessunit_list'),
    path('businessunit/add/', views.businessunit_change, name='businessunit_add'),
    re_path('businessunit/edit/(?P<pk>\d+)/', views.businessunit_change, name='businessunit_edit'),
    re_path('businessunit/delete/(?P<pk>\d+)/', views.businessunit_delete, name='businessunit_delete'),


    path('server/', views.server_list, name='server_list'),
    path('server/add/', views.server_change, name='server_add'),
    re_path('server/edit/(?P<pk>\d+)/', views.server_change, name='server_edit'),
    re_path('server/delete/(?P<pk>\d+)/', views.server_delete, name='server_delete'),
    re_path('server/detail/(?P<pk>\d+)/', views.server_detail, name='server_detail'),
    re_path('server/asset_change_list/(?P<pk>\d+)/', views.server_asset_change_list, name='server_asset_change_list'),
]
