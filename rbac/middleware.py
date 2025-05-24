from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect, reverse, render, HttpResponse
import re


class RBACMiddleware(MiddlewareMixin):

    def process_request(self, request):
        white_list = ['/web/login/', ]
        if request.path_info in white_list:
            return None
        else:
            permission_list = request.session['permissions']
            if permission_list:
                for url_pattern in permission_list:
                    match = re.match('/'+url_pattern, request.path_info)
                    if match:
                        print(match)
                        return None
                return HttpResponse('无权访问')
        return redirect(reverse('web:login'))
