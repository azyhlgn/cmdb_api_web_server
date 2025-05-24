import json

from django.shortcuts import render, redirect, reverse
from django.views.decorators.csrf import csrf_exempt

from repository import models
from rbac.models import UserInfo
from web import forms


# Create your views here.
def index(request):
    return render(request, 'index.html', )


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = UserInfo.objects.filter(username=username, password=password)
        if user:
            permissions = list(user.values_list('role__permission__url_pattern', flat=True).distinct())
            menu_data = user.filter(role__permission__is_changelist=True).values_list('role__permission__menu_name',
                                                                                      'role__permission__title',
                                                                                      'role__permission__url_pattern')
            menu_dict = {}
            for p_menu, s_menu, s_menu_url in menu_data:
                if p_menu not in menu_dict:
                    menu_dict[p_menu] = [[s_menu, s_menu_url], ]
                else:
                    menu_dict[p_menu].append([s_menu, s_menu_url])
            request.session['permissions'] = permissions
            request.session['menu_dict'] = menu_dict
            request.session['userinfo'] = {'username': user.first().username, 'userid': user.first().id}
            print(request.session['userinfo'])

            return redirect(reverse('web:index'))
    return render(request, 'login.html')
