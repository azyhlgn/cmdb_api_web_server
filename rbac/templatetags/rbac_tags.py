import pprint
from collections import OrderedDict
from django.shortcuts import render, redirect, reverse
from django.template import Library
from rbac.models import Role, UserInfo, Permission

register = Library()


def userinfo_list(request):
    datalist = UserInfo.objects.all()
    """<a href="%s" class="list-group-item">%s</a>"""
    query_dict = request.GET.copy()
    query_dict.mutable = True

    user_id = query_dict.get('user_id')
    for item in datalist:

        if user_id and int(item.id) == int(user_id):
            query_dict.pop('user_id')
            yield '<a href="?%s" class="list-group-item active" style="text-decoration:none;color:inherit;">%s</a>' % (
                query_dict.urlencode(), item.username)
        else:
            query_dict['user_id'] = item.id
            yield '<a href="?%s" class="list-group-item" style="text-decoration:none;color:inherit;">%s</a>' % (
                query_dict.urlencode(), item.username)


def role_list(request):
    """<a href="?%s" class="list-group-item"
    style="display: flex;align-items: center;justify-content: space-between">%s
    <input type="checkbox"></a>"""

    datalist = Role.objects.all()
    query_dict = request.GET.copy()
    query_dict.mutable = True

    role_id = query_dict.get('role_id')
    # 判断checkbox是否checked
    user_id = query_dict.get('user_id')
    if user_id:
        user_obj = UserInfo.objects.get(id=user_id)
        if user_obj:
            role_checked = list(user_obj.role.values_list('id', flat=True))
        else:
            role_checked = None
    else:
        role_checked = None

    for item in datalist:
        if role_id and int(item.id) == int(role_id):
            query_dict.pop('role_id')
            if role_checked and item.id in role_checked:
                yield '''<a href="?%s" class="list-group-item active"
                        style="display: flex;align-items: center;justify-content: space-between;text-decoration:none;color:inherit;">%s
                        <input type="checkbox" name="%s" value="%s" checked></a>''' % (
                    query_dict.urlencode(), item.name, 'role_id', item.id)
            else:
                yield '''<a href="?%s" class="list-group-item active"
        style="display: flex;align-items: center;justify-content: space-between;text-decoration:none;color:inherit;">%s
        <input type="checkbox" name="%s" value="%s"></a>''' % (query_dict.urlencode(), item.name, 'role_id', item.id)
        else:
            query_dict['role_id'] = item.id
            if role_checked and item.id in role_checked:
                yield '''<a href="?%s" class="list-group-item"
                        style="display: flex;align-items: center;justify-content: space-between;text-decoration:none;color:inherit;">%s
                        <input type="checkbox" name="%s" value="%s" checked></a>''' % (
                    query_dict.urlencode(), item.name, 'role_id', item.id)
            else:
                yield '''<a href="?%s" class="list-group-item "
    style="display: flex;align-items: center;justify-content: space-between;text-decoration:none;color:inherit;">%s
    <input type="checkbox" name="%s" value="%s"></a>''' % (query_dict.urlencode(), item.name, 'role_id', item.id)


def permission_list(request):
    """<li class="list-group-item"
    style="display: flex;align-items: center;justify-content: space-between">{{ item }}
    <input type="checkbox"></li>"""

    # 构建页面显示时需要的数据结构 一级菜单>二级菜单changelist>附属url
    data_dict = OrderedDict()
    primary_menu_list = list(Permission.objects.all().values_list('menu_name', flat=True).distinct())
    primary_menu_list.remove(None)
    primary_menu_list.append('其他')
    for primary_menu in primary_menu_list:
        if primary_menu == '其他':
            secondary_menu_list = Permission.objects.filter(is_changelist=False, parent_url_pattern=None)
            data_dict[primary_menu] = secondary_menu_list
        else:
            secondary_menu_list = Permission.objects.filter(menu_name=primary_menu, is_changelist=True)
            secondary_dict = OrderedDict()
            for secondary_menu in secondary_menu_list:
                sub_menu = Permission.objects.filter(parent_url_pattern=secondary_menu)
                secondary_dict[secondary_menu] = sub_menu
            data_dict[primary_menu] = secondary_dict

    # 整理判断checkbox是否checked的数据
    role_id = request.GET.get('role_id')
    if role_id:
        role_obj = Role.objects.get(id=role_id)
        if role_obj:
            permission_checked = list(role_obj.permission.values_list('id', flat=True))
        else:
            permission_checked = None
    else:
        permission_checked = None

    for primary_menu, secondary_menu_dict in data_dict.items():
        yield '''<li class="list-group-item list-group-item-secondary"
        style="display: flex;align-items: center;justify-content: space-between">%s</li>''' % primary_menu

        if primary_menu != '其他':
            # 构建普通的二级与附属url显示
            for secondary_menu, sub_menu_list in secondary_menu_dict.items():
                # yield '''<li class="list-group-item"
                #         style="display: flex;align-items: center;justify-content: space-between">----%s
                #         <input type="checkbox"></li>''' % secondary_menu
                yield '''<li class="list-group-item">'''
                if permission_checked and secondary_menu.id in permission_checked:
                    yield '''<span style="margin-left"><span style="margin-right:5px;">
                                %s</span><input type="checkbox" checked name="%s" value="%s"></span>''' % (
                        secondary_menu.title, 'permission_id', secondary_menu.id)
                else:
                    yield '''<span style="margin-left"><span style="margin-right:5px;">
                %s</span><input type="checkbox" name="%s" value="%s"></span>''' % (
                        secondary_menu.title, 'permission_id', secondary_menu.id)
                yield '''<div style="display: flex;align-items: center;justify-content: space-between">'''
                for sub_menu in sub_menu_list:
                    if permission_checked and sub_menu.id in permission_checked:
                        yield '''<small style="display: flex;align-items: center;justify-content: space-between;
                                        margin-left:10px;"><span style="margin-right:5px;">%s</span>
                                        <input type="checkbox" checked name="%s" value="%s"></small>''' % (
                            sub_menu.title, 'permission_id', sub_menu.id)
                    else:
                        yield '''<small style="display: flex;align-items: center;justify-content: space-between;
                    margin-left:10px;"><span style="margin-right:5px;">%s</span>
                    <input type="checkbox" name="%s" value="%s"></small>''' % (
                            sub_menu.title, 'permission_id', sub_menu.id)
                yield '''</div></li>'''
        else:
            # 构建其他url展示
            yield '''<li class="list-group-item">'''
            yield '''<div style="display: flex;align-items: center;justify-content: left;flex-wrap:wrap;">'''
            for secondary_menu in secondary_menu_dict:
                if permission_checked and secondary_menu.id in permission_checked:
                    yield '''<small style="display: flex;align-items: center;justify-content: space-between;
                                    margin-left:10px;"><span style="margin-right:5px;">%s</span>
                                    <input type="checkbox" checked name="%s" value="%s"></small>''' % (
                        secondary_menu.title, 'permission_id', secondary_menu.id)
                else:
                    yield '''<small style="display: flex;align-items: center;justify-content: space-between;
                margin-left:10px;"><span style="margin-right:5px;">%s</span>
                <input type="checkbox" name="%s" value="%s"></small>''' % (
                        secondary_menu.title, 'permission_id', secondary_menu.id)
            yield '''</div></li>'''


# def menu_list(request):
#     menu_dict = request.session['menu_dict']
#
#     print(menu_dict)
#     for p_menu, s_menu_list in menu_dict.items():
#         yield '''<a href="/web/index/" class="active">%s</a>''' % p_menu
#         for s_menu in s_menu_list:
#             yield '''<sm href="/web/index/" class="active">%s</sm>''' % s_menu
#

@register.inclusion_tag('rbac/userinfo_card.html')
def userinfo_card(request):
    userinfo = userinfo_list(request)
    return {'userinfo': userinfo}


@register.inclusion_tag('rbac/role_card.html')
def role_card(request):
    role = role_list(request)
    query_dict = request.GET.copy()
    query_dict.mutable = True
    query_dict['post_type'] = 'role_distribution'
    form_action = query_dict.urlencode()
    return {'role': role, 'form_action': form_action}


@register.inclusion_tag('rbac/permission_card.html')
def permission_card(request):
    permission = permission_list(request)
    query_dict = request.GET.copy()
    query_dict.mutable = True
    query_dict['post_type'] = 'permission_distribution'
    form_action = query_dict.urlencode()
    return {'permission': permission, 'form_action': form_action}


@register.inclusion_tag('rbac/sidebar_menu.html')
def sidebar_menu(request):
    # menu = menu_list(request)
    menu_dict = request.session['menu_dict']
    # return {'menu': menu}
    return {'menu_dict': menu_dict}


@register.inclusion_tag('rbac/breadcrumb.html')
def breadcrumb(request):
    userinfo = request.session['userinfo']
    url_pattern = request.resolver_match.route
    breadcrumb_list = []
    permission_obj = Permission.objects.filter(url_pattern=url_pattern).first()
    if permission_obj.title != '首页':
        breadcrumb_list.append(['web/index/', '首页'])
    if permission_obj.is_changelist:
        breadcrumb_list.append([permission_obj.url_pattern, permission_obj.title])
    else:
        if permission_obj.parent_url_pattern:
            parent_url = permission_obj.parent_url_pattern
            breadcrumb_list.extend(
                [[parent_url.url_pattern, parent_url.title], [permission_obj.url_pattern, permission_obj.title]])
        else:
            breadcrumb_list.append([permission_obj.url_pattern, permission_obj.title])

    return {'breadcrumb_list': breadcrumb_list, 'userinfo': userinfo}
