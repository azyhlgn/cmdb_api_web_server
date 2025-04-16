from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import json

from rest_framework.views import APIView
from rest_framework.response import Response

from repository import models
from API.lib.saver.saver import my_saver


class Asset(APIView):

    def get(self, request):
        # host_list = ['192.168.22.129', '192.168.22.129', '192.168.22.129', ]
        host_list = ['192.168.22.129']
        return Response(host_list)

    def post(self, request):
        # print(json.dumps(request.data))
        request_data = request.data
        server = None
        for key, value in request_data.items():
            if key == 'Basic':
                server = models.Server.objects.filter(**value['data'])
                if not server:
                    print('sever新增')
                    server = models.Server.objects.create(**value['data'])
            if key == 'MainBoard':
                server.update(**value['data'])
            if key == 'Cpu':
                server.update(**value['data'])
            if key == 'Memory' or key == 'Disk':
                my_saver.save(server, value['data'], key,'slot')
            if key == 'NIC':
                my_saver.save(server, value['data'], key, 'name')

        return Response('收到收到收到')
