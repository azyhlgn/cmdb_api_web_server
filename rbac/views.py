from django.urls import get_resolver, URLPattern
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, reverse
import pprint

from rbac.forms import PermissionForm
from rbac.models import Permission, UserInfo, Role


# Create your views here.

def get_all_urls(urlpatterns, ignore_namespace_list=None):
    if not ignore_namespace_list:
        ignore_namespace_list = []
    url_patterns = []
    for url in urlpatterns:
        if isinstance(url, URLPattern):
            url_patterns.append({'url_pattern': str(url.pattern), 'reverse_name': str(url.name)})
        else:
            if url.namespace in ignore_namespace_list:
                continue
            sub_url_patterns = get_all_urls(url.url_patterns)
            new_sub_url_patterns = []
            for sub_url_dict in sub_url_patterns:
                if url.namespace and sub_url_dict['reverse_name'] != 'None':
                    new_sub_url_patterns.append(
                        {
                            'url_pattern': ''.join((str(url.pattern), sub_url_dict['url_pattern'])),
                            'reverse_name': ':'.join((str(url.namespace), sub_url_dict['reverse_name'])),
                        })
                else:
                    new_sub_url_patterns.append(
                        {
                            'url_pattern': ''.join((str(url.pattern), sub_url_dict['url_pattern'])),
                            'reverse_name': sub_url_dict['reverse_name'],
                        }
                    )

            url_patterns.extend(new_sub_url_patterns)

    return url_patterns


def permission_multi(request):
    # 递归查询所有的url
    all_url = get_all_urls(get_resolver().url_patterns, ignore_namespace_list=['admin', 'api'])
    set1 = set([i['url_pattern'] for i in all_url])
    # 查询数据库中所有url
    db_url = Permission.objects.all().values_list('url_pattern', flat=True)
    set2 = set(db_url)

    # 需要新建的url
    add_set = set1 - set2
    add_url = [i for i in all_url if i['url_pattern'] in add_set]
    add_mfs = modelformset_factory(model=Permission, form=PermissionForm, extra=len(add_set))
    add_form_set = add_mfs(queryset=Permission.objects.none(), initial=add_url)

    # 需要删除的url
    del_set = set2 - set1
    del_mfs = modelformset_factory(model=Permission, form=PermissionForm, extra=0)
    del_form_set = del_mfs(queryset=Permission.objects.filter(('url_pattern__in', del_set)))

    # 可以用于编辑的已存在url
    edit_set = set1 and set2
    edit_mfs = modelformset_factory(model=Permission, form=PermissionForm, extra=0)
    edit_form_set = edit_mfs(queryset=Permission.objects.filter(('url_pattern__in', edit_set)))

    context = {
        'add_form_set': add_form_set,
        'del_form_set': del_form_set,
        'edit_form_set': edit_form_set,
    }

    post_type = request.GET.get('post_type')

    if request.method == 'POST' and post_type == 'add':
        add_mfs = modelformset_factory(model=Permission, form=PermissionForm, extra=0)
        add_form_set = add_mfs(request.POST)
        if add_form_set.is_valid():
            add_form_set.save()
            return redirect('rbac:permission_multi')
        context['add_form_set'] = add_form_set

    if request.method == 'POST' and post_type == 'del':
        del_mfs = modelformset_factory(model=Permission, form=PermissionForm, extra=0)
        del_form_set = del_mfs(request.POST)
        form_num = request.POST.get('form-TOTAL_FORMS')
        if int(form_num) > 0:
            form_list = []
            for i in range(int(form_num)):
                form_list.append(request.POST.get('form-%s-url_pattern' % i))

            Permission.objects.filter(url_pattern__in=form_list).delete()
        return redirect(reverse('rbac:permission_multi'))

    if request.method == 'POST' and post_type == 'edit':
        edit_mfs = modelformset_factory(model=Permission, form=PermissionForm, extra=0)
        edit_form_set = edit_mfs(request.POST)
        if edit_form_set.is_valid():
            edit_form_set.save()
            return redirect('rbac:permission_multi')
        context['edit_form_set'] = edit_form_set

    return render(request, 'rbac/permission_multi.html', context)


def permission_distribution(request):
    if request.method == 'POST':
        post_type = request.GET.get('post_type')
        if post_type == 'role_distribution':
            user_id = request.GET.get('user_id')
            if user_id:
                user = UserInfo.objects.get(pk=user_id)
                role_list = request.POST.getlist('role_id')
                if user and role_list:
                    user.role.set(role_list)
                    user.save()
                elif user and not role_list:
                    user.role.clear()
                    user.save()
            query_dict = request.GET.copy()
            query_dict.mutable = True
            query_dict.pop('post_type')
            return redirect(reverse('rbac:permission_distribution') + '?' + query_dict.urlencode())

        if post_type == 'permission_distribution':
            role_id = request.GET.get('role_id')
            if role_id:
                role = Role.objects.get(pk=role_id)
                permission_list = request.POST.getlist('permission_id')
                if role and permission_list:
                    role.permission.set(permission_list)
                    role.save()
                elif role and not permission_list:
                    role.permission.clear()
                    role.save()
            query_dict = request.GET.copy()
            query_dict.mutable = True
            query_dict.pop('post_type')
            return redirect(reverse('rbac:permission_distribution') + '?' + query_dict.urlencode())

    return render(request, 'rbac/permission_distribution.html', {'request': request})
