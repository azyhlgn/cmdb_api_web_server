from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.response import Response


class Asset(APIView):

    def get(self, request):
        # host_list = ['192.168.22.129', '192.168.22.129', '192.168.22.129', ]
        host_list = ['192.168.22.129']
        return Response(host_list)

    def post(self, request):
        print(request.data)
        return Response('收到收到收到')
