from django.shortcuts import render, redirect, reverse
from django.views.decorators.csrf import csrf_exempt

from repository import models
from WEB import forms


# Create your views here.
def index(request):
    return render(request, 'index.html')


def server_list(request):
    data_list = models.Server.objects.all().order_by('pk')
    return render(request, 'Server_list.html', {'data_list': data_list})


@csrf_exempt
def server_change(request, pk=None):
    obj = models.Server.objects.filter(pk=pk).first()
    if request.method == 'POST':
        form_obj = forms.ServerForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('web:server_list'))
    form_obj = forms.ServerForm(instance=obj)
    return render(request, 'Server_add.html', {'form_obj': form_obj})


def server_delete(request, pk=None):
    models.Server.objects.filter(pk=pk).delete()
    return redirect(reverse('web:server_list'))


def server_detail(request, pk=None):
    obj = models.Server.objects.filter(pk=pk).first()
    nic_list = obj.nic_list.all().order_by('pk')
    disk_list = obj.disk_list.all().order_by('pk')
    memory_list = obj.memory_list.all().order_by('pk')

    return render(request, 'Server_detail.html', {
        'obj': obj,
        'nic_list': nic_list,
        'disk_list': disk_list,
        'memory_list': memory_list,
    })


def server_asset_change_list(request, pk=None):
    obj = models.Server.objects.filter(pk=pk).first()
    asset_change_list = obj.asset_change_list.all().order_by('pk')

    return render(request, 'Asset_change_list.html', {'asset_change_list': asset_change_list, })


def businessunit_list(request):
    data_list = models.BusinessUnit.objects.all().order_by('pk')
    return render(request, 'BusinessUnit_list.html', {'data_list': data_list})


@csrf_exempt
def businessunit_change(request, pk=None):
    obj = models.BusinessUnit.objects.filter(pk=pk).first()
    if request.method == 'POST':
        form_obj = forms.BusinessUnitForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('web:businessunit_list'))
    form_obj = forms.BusinessUnitForm(instance=obj)
    return render(request, 'BusinessUnit_add.html', {'form_obj': form_obj})


def businessunit_delete(request, pk=None):
    models.BusinessUnit.objects.filter(pk=pk).delete()
    return redirect(reverse('web:businessunit_list'))
