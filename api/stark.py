import time

from stark.service.stark import site
from repository import models
from stark.service.stark import StarkModelConfig, Option
from django.urls import path, re_path
from django.shortcuts import HttpResponse, render
from django.utils.safestring import mark_safe
import functools
from api.lib.conn_pool.redis_conn_pool import redis_pool
import redis
import pickle
from hashlib import md5

from repository.lib.data_excutor.data_excutor import get_name_value_form_field


def xxxx(request):
    return HttpResponse("xxxxxx")


def yyyy(request):
    return HttpResponse("yyyyyy")


class ServerConfig(StarkModelConfig):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 构造redis键
        self.redis_key_prefix = ':'.join(
            (self.model_cls._meta.app_label,
             self.model_cls._meta.model_name,
             )
        )
        print(self.redis_key_prefix)

    def show_details(self, request, pk):
        # 得到服务器信息
        server = self.model_cls.objects.get(pk=pk)
        server_field_name_list = [field.name for field in server._meta.fields]
        server_value_list = []
        for field_name in server_field_name_list:
            server_value_list.append(getattr(server, field_name))
        print(server_value_list)
        server_data = {
            'name': server_field_name_list,
            'value': server_value_list,
        }

        # todo 得到服务器相关资源信息  disk memory nid
        disk_qs = models.Disk.objects.filter(server=server)
        disk_data = get_name_value_form_field(disk_qs, 'Disk','服务器硬盘信息')
        memory_qs = models.Memory.objects.filter(server=server)
        memory_data = get_name_value_form_field(memory_qs, 'Memory','服务器内存信息')
        nic_qs = models.NIC.objects.filter(server=server)
        nic_data = get_name_value_form_field(nic_qs, 'NIC','服务器网卡信息')

        # 返回结果
        content = {
            'server_data': server_data,
            'other_info': {
                'disk_data': disk_data,
                'memory_data': memory_data,
                'nic_data': nic_data,
            }
        }
        return render(request, 'show_details.html', content)

    def extra_urls(self):
        urlpatterns = [
            path('xxx/', xxxx),
            path('yyy/', yyyy),
            re_path('(?P<pk>\d+)/', self.show_details),
        ]
        return urlpatterns

    def display_detail(self, row=None, header=False):
        if header:
            return '查看详细信息'
        return mark_safe('<a class="btn btn-primary" href="/stark/repository/server/%s/">查看</a>' % (row.id))

    display_list = [StarkModelConfig.display_checkbox, display_detail, 'sn', 'hostname', 'business_unit',
                    'device_status_id',
                    StarkModelConfig.display_edit_delete]
    multi_action_list = [StarkModelConfig.mulit_delete, StarkModelConfig.mulit_init]
    search_field_list = ['business_unit__name', 'sn']

    combinatorial_search_field_list = [
        Option('device_status_id', is_choice=True),
        Option('hostname', condition={'id__gt': 5}, text='hostname', value='hostname'),
        Option('business_unit', text='name', value='pk', multi_select=True),
    ]

    # 实现读取 旁路缓存
    def get_queryset(self):
        # 构建redis key
        redis_key = self.redis_key_prefix + ':' + md5(str(self.request.GET.get('q')).encode()).hexdigest()
        # 查询缓存 命中则返回 未命中则读数据库并写缓存
        # 使用redis连接池 避免每次访问url都需要重新连接 浪费资源
        conn = redis.Redis(connection_pool=redis_pool)
        data = conn.get(redis_key)
        if data:
            print('redis read')
            return pickle.loads(data)

        result = super().get_queryset()
        print('sql read')
        data = pickle.dumps(result)
        conn.set(redis_key, data)
        return result

    # 实现更新双删
    def wrapper(self, func, *args, **kwargs):
        @functools.wraps(func)
        def inner(request, *args, **kwargs):
            self.request = request

            if request.method == 'POST':
                # 更新操作 延迟双删
                # 连接
                conn = redis.Redis(connection_pool=redis_pool)
                print('redis del 1')
                # 一删除缓存
                keys = conn.keys(self.redis_key_prefix.rsplit(':', 1)[0] + '*')
                if len(keys) > 0:
                    conn.delete(*keys)
                # 更新数据库
                result = func(request, *args, **kwargs)
                # 延迟
                time.sleep(0.3)
                # 第二次删除
                keys = conn.keys(self.redis_key_prefix.rsplit(':', 1)[0] + '*')
                if len(keys) > 0:
                    conn.delete(*keys)
                    print('redis del 2')
                return result

            result = func(request, *args, **kwargs)
            return result

        return inner


class BusinessUnitConfig(StarkModelConfig):
    search_field_list = ['id']


site.register(models.Server, ServerConfig)
site.register(models.BusinessUnit, BusinessUnitConfig)
