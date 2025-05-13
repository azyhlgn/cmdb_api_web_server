from stark.service.stark import site
from repository import models
from stark.service.stark import StarkModelConfig, Option
from django.urls import path, re_path
from django.shortcuts import HttpResponse
from django.utils.safestring import mark_safe


def xxxx(request):
    return HttpResponse("xxxxxx")


def yyyy(request):
    return HttpResponse("yyyyyy")


class ServerConfig(StarkModelConfig):

    def extra_urls(self):
        urlpatterns = [
            path('xxx/', xxxx),
            path('yyy/', yyyy),
        ]
        return urlpatterns

    display_list = [StarkModelConfig.display_checkbox, 'sn', 'hostname', 'business_unit', 'device_status_id',
                    StarkModelConfig.display_edit_delete]
    multi_action_list = [StarkModelConfig.mulit_delete, StarkModelConfig.mulit_init]
    search_field_list = ['business_unit__name', 'sn']

    combinatorial_search_field_list = [
        Option('device_status_id', is_choice=True),
        Option('hostname', condition={'id__gt': 5}, text='hostname', value='hostname'),
        Option('business_unit', text='name', value='pk', multi_select=True),
    ]


class BusinessUnitConfig(StarkModelConfig):
    search_field_list = ['id']


site.register(models.Server, ServerConfig)
site.register(models.BusinessUnit, BusinessUnitConfig)
