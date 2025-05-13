import functools

from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import HttpResponse, render, redirect, reverse
from django.utils.safestring import mark_safe
from types import FunctionType
from django.db.models import Q, ForeignKey
from django.http import QueryDict
from ..form import BaseForm
from ..utils.pagination import Pagination


class Row(object):
    def __init__(self, data_list, option, query_dict):
        """
        用于遍历datalist并生成渲染后的html语句
        :param data_list: 用于%s赋值于html语句的数据列表 其中的元素均为二元元组 [(xy,z),(ab,c),]
        :param option:
        :param query_dict:config经option传入row的request.GET参数
        """

        # queryset转set去重 防止出现两个(None,None)去重失败的情况 直接self.data_list = set(data_list) 页面的内容顺序会每次都不一样
        self.data_list = []
        unique = set()
        for data in data_list:
            if data not in unique:
                unique.add(data)
                self.data_list.append(data)
        print(self.data_list)
        self.option = option
        self.query_dict = query_dict

    def __iter__(self):

        yield '<div>'
        yield '<span>%s:</span>' % self.option.field_verbose_name
        qd = self.query_dict.copy()
        qd.mutable = True
        if self.option.field_name in qd:
            qd.pop(self.option.field_name)
            yield '<a class="btn btn-light" href="?%s">全部</a>' % qd.urlencode()
        else:
            yield '<a class="btn btn-info" href="?%s">全部</a>' % qd.urlencode()

        for data in self.data_list:
            qd = self.query_dict.copy()
            qd.mutable = True
            if 'page' in qd:
                qd.pop('page')
            qd_list = self.query_dict.getlist(self.option.field_name)
            # print(data[0],qd_list)
            if str(data[0]) in qd_list:
                if self.option.multi_select:
                    qd_list.remove(str(data[0]))

                    qd.setlist(self.option.field_name, qd_list)
                else:
                    qd.pop(self.option.field_name)
                yield '<a class="btn btn-info" href="?%s">%s</a>' % (qd.urlencode(), data[1])
            else:
                if self.option.multi_select:
                    qd_list.append(data[0])
                    qd.setlist(self.option.field_name, qd_list)
                else:
                    qd[self.option.field_name] = data[0]
                yield '<a class="btn btn-light" href="?%s">%s</a>' % (qd.urlencode(), data[1])
        yield '</div>'


class Option(object):
    def __init__(self, field_name, condition=None, is_choice=False, text=None, value=None, multi_select=False):
        """
        用于组合搜索功能
        :param field_name: 字段名称
        :param condition: 需要收集字段数据的样本的筛选条件
        :param is_choice: 是否是choice类型
        :param text: 指定字段的文字字段
        :param value: 指定字段的value值的字段
        """
        self.field_name = field_name
        if condition is None:
            self.condition = {}
        else:
            self.condition = condition
        self.is_choice = is_choice
        self.text = text
        self.value = value
        self.field_verbose_name = None
        self.multi_select = multi_select

    def get_queryset(self, config, queryset, query_dict):
        # 查询此个字段 在本model中 所有出现过的值
        # 先实现字段的显示 普通field 和 choice
        field = config.model_cls._meta.get_field(self.field_name)
        self.field_verbose_name = field.verbose_name
        # 如果是外键 就要统计本model中 出现过的fk值的集合
        if isinstance(field, ForeignKey):
            # 构造用于values_list的搜索条件
            filter_tuple = (self.field_name + '__' + self.value, self.field_name + '__' + self.text)
            data_list = queryset.filter(**self.condition).values_list(*filter_tuple).distinct()
            return Row(data_list, self, query_dict)
        else:
            # 如果时choices 就应该返回出现过的选择集合 简单的返回choices会导致前端页面出现会返回空数据页面的搜索按钮选择
            # 取值？
            # 为了方便的话 可以直接返回choices 但是choices是一个包含元组数据的列表 对这个列表的所有数据都有一个共同的取值模式
            # 遍历这个列表 并且取第二个值 也就是lambda x: x[1]
            if field.choices:
                return Row(field.choices, self, query_dict)
            else:
                # 如果是普通field 应该返回的是model中 在q搜索条件下 这个field的值的集合 不可重复
                # 取值 应该是使用value_list 并且去重 返回一个可迭代的列表
                filter_tuple = (self.value, self.text)
                data_list = queryset.filter(**self.condition).values_list(*filter_tuple).distinct()
                return Row(data_list, self, query_dict)


class ChangeListVO(object):
    def __init__(self, config):
        self.config = config

        self.list_display = self.config.get_display_list()
        self.queryset, self.q = self.config.get_queryset()

        # 处理组合搜索
        # 构造组合搜索需要的查询字典
        conn = Q()
        conn.connector = 'and'
        # 判断是否有定义 combinatorial_search_field_list
        if self.config.combinatorial_search_field_list:
            for option in self.config.combinatorial_search_field_list:
                val_list = self.config.request.GET.getlist(option.field_name)
                if val_list:
                    # todo
                    # 处理val为None的情况
                    if 'None' in val_list:
                        print(val_list)
                        # 处理request.GET中某个字段的列表值中含有None 例如 [1,2,3,None]
                        # 需要构建搜索条件为 'my_field__in'=[1,2,3] or 'my_field__isnull'=True
                        has_none_q = Q()
                        has_none_q.connector = 'or'

                        has_none_q.children.append(('%s__isnull' % option.field_name, True))
                        # 从val中pop掉None值 若不为空 再使用 __in 构造搜索条件
                        val_list.remove('None')
                        if val_list:
                            print('1111')
                            has_none_q.children.append(('%s__in' % option.field_name, val_list))
                        conn.children.append(has_none_q)
                    else:
                        conn.children.append(('%s__in' % option.field_name, val_list))
            print(conn.children)
        self.queryset = self.queryset.filter(conn)

        # 处理分页并分割queryset数据
        page_param = self.config.request.GET.get('page')
        total_count = self.queryset.count()
        qdict = self.config.request.GET.copy()
        qdict.mutable = True
        # 用于产出数据起始和结束的索引 和html的分页组件渲染
        self.page = Pagination(page_param, total_count, self.config.request.path_info, qdict, per_page=5)
        self.queryset = self.queryset[self.page.start:self.page.end]

        # 处理需要显示的批量处理按钮
        self.multi_action_list = self.config.get_multi_action_list()

        # 判断是否显示'新增'按钮
        if self.config.add_btn:
            add_btn_obj = self.config.display_add_btn()
            self.add_btn_obj = add_btn_obj

        # 判断是否显示搜索功能 和保存搜索条件
        if self.config.get_search_field_list():
            self.search_field_list = self.config.get_search_field_list()


class StarkModelConfig(object):

    def mulit_delete(self):
        pk_list = self.request.POST.getlist('pk')
        self.model_cls.objects.filter(pk__in=pk_list).delete()
        return HttpResponse('批量删除成功')

    mulit_delete.text = '批量删除'

    def mulit_init(self):
        print('批量初始化运行中')

    mulit_init.text = '批量初始化'

    # multi_action_list = [mulit_delete, mulit_init]
    multi_action_list = []
    display_list = []
    search_field_list = []
    combinatorial_search_field_list = []
    order_by = ['id', ]

    model_form_cls = None
    add_btn = True

    def __init__(self, model_cls, site):
        self.model_cls = model_cls
        self.site = site
        self.request = None

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        # 构造Q查询条件
        conn = Q()
        conn.connector = 'or'
        if q:
            for field in self.get_search_field_list():
                # 根据设定的搜索字段 在Q中增加条件
                conn.children.append(('%s__contains' % field, q))

        return self.model_cls.objects.filter(conn).order_by(*self.get_order_by()), q

    def get_display_list(self):
        return self.display_list

    def get_search_field_list(self):
        return self.search_field_list

    def get_order_by(self):
        return self.order_by

    def get_reverse_edit_url(self, row):
        namespace = self.site.namespace
        app_label = self.model_cls._meta.app_label
        model_name = self.model_cls._meta.model_name
        url = reverse('%s:%s_%s_change' % (namespace, app_label, model_name), args=(row.pk,))
        if not self.request.GET:
            return url

        params_str = self.request.GET.urlencode()  # q=xxx&page=2

        new_query_dict = QueryDict(mutable=True)
        new_query_dict['_filter'] = params_str

        return url + '?' + new_query_dict.urlencode()

    def get_reverse_delete_url(self, row):
        namespace = self.site.namespace
        app_label = self.model_cls._meta.app_label
        model_name = self.model_cls._meta.model_name
        url = reverse('%s:%s_%s_delete' % (namespace, app_label, model_name), args=(row.pk,))

        if not self.request.GET:
            return url

        params_str = self.request.GET.urlencode()  # q=xxx&page=2

        new_query_dict = QueryDict(mutable=True)
        new_query_dict['_filter'] = params_str

        return url + '?' + new_query_dict.urlencode()

    def get_reverse_add_url(self):
        namespace = self.site.namespace
        app_label = self.model_cls._meta.app_label
        model_name = self.model_cls._meta.model_name
        url = reverse('%s:%s_%s_add' % (namespace, app_label, model_name))

        if not self.request.GET:
            return url

        params_str = self.request.GET.urlencode()  # q=xxx&page=2

        new_query_dict = QueryDict(mutable=True)
        new_query_dict['_filter'] = params_str

        return url + '?' + new_query_dict.urlencode()

    def get_reverse_changelist_url(self):
        namespace = self.site.namespace
        app_label = self.model_cls._meta.app_label
        model_name = self.model_cls._meta.model_name
        url = reverse('%s:%s_%s_changelist' % (namespace, app_label, model_name))
        params = self.request.GET.urlencode()
        _filter = self.request.GET.get('_filter', '')

        if _filter:
            return url + '?' + _filter
        if params:
            return url + '?' + params

        return url

    @property
    def get_change_form(self):

        if self.model_form_cls:
            return self.model_form_cls

        class ChangeModelForm(BaseForm):
            class Meta:
                model = self.model_cls
                fields = '__all__'

        return ChangeModelForm

    def get_multi_action_list(self):

        return [{'func_name': action.__name__, 'func_text': action.text} for action in self.multi_action_list if
                self.multi_action_list]

    def get_combinatorial_search_field_list(self):
        return self.combinatorial_search_field_list

    def display_checkbox(self, row=None, header=False):
        if header:
            return '选择'
        return mark_safe('<input type="checkbox" name="pk" value="%s" />' % row.pk)

    def display_edit(self, row=None, header=False):
        if header:
            return '操作'
        return mark_safe('<a class="btn btn-primary" href="%s">编辑</a>' % self.get_reverse_edit_url(row))

    def display_delete(self, row=None, header=False):
        if header:
            return '操作'
        return mark_safe('<a class="btn btn-danger" href="%s">删除</a>' % self.get_reverse_delete_url(row))

    def display_edit_delete(self, row=None, header=False):
        if header:
            return '操作'
        tpl = '<a class="btn btn-primary" href="%s">编辑</a>|<a class="btn btn-danger" href="%s">删除</a>' % (
            self.get_reverse_edit_url(row), self.get_reverse_delete_url(row))
        return mark_safe(tpl)

    def display_add_btn(self):
        tpl = '''<div style="float: left"><a href="%s"><button class="btn btn-success" style="margin-bottom: 5px;">新增</button></a></div>''' % self.get_reverse_add_url()
        return mark_safe(tpl)

    def changelist_views(self, request):

        # 用于处理批量操作
        if request.method == 'POST':
            action = request.POST.get('action')
            func = getattr(self, action, None)
            if func:
                response = getattr(self, action)()
                if response:
                    return response
            return redirect(self.get_reverse_changelist_url())

        queryset, q = self.get_queryset()

        # 构造渲染页面需要的VO
        vo = ChangeListVO(self)

        # 构建组合搜索需要用的数据
        combinatorial_search_field_list = self.get_combinatorial_search_field_list()
        combinatorial_search_field_data = []  # 用于赋值给vo并在之后用于html中渲染的数据 列表中的元素均为Row的实例
        for opts in combinatorial_search_field_list:
            combinatorial_search_field_data.append(opts.get_queryset(self, queryset, request.GET))

        # 赋值给vo
        vo.combinatorial_search_field_data = combinatorial_search_field_data
        context = {
            'vo': vo,
        }
        return render(request, 'stark/changelist.html', context)

    @csrf_exempt
    def change_views(self, request, pk=None):
        obj = self.model_cls.objects.filter(pk=pk).first()
        if request.method == 'GET':
            form_obj = self.get_change_form(instance=obj)
            return render(request, 'stark/change.html', {'form_obj': form_obj})

        form_obj = self.get_change_form(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(self.get_reverse_changelist_url())
        return render(request, 'stark/change.html', {'form_obj': form_obj})

    @csrf_exempt
    def add_views(self, request):
        if request.method == 'GET':
            form_obj = self.get_change_form()
            return render(request, 'stark/change.html', {'form_obj': form_obj})

        form_obj = self.get_change_form(request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(self.get_reverse_changelist_url())
        return render(request, 'stark/change.html', {'form_obj': form_obj})

    def delete_views(self, request, pk=None):
        if request.method == 'GET':
            return render(request, 'stark/delete.html',
                          {
                              'pk': pk,
                              'cancel_url': self.get_reverse_changelist_url()
                          })
        self.model_cls.objects.filter(pk=pk).delete()
        return redirect(self.get_reverse_changelist_url())

    def extra_urls(self):
        return None

    def get_urls(self):
        info = self.model_cls._meta.app_label, self.model_cls._meta.model_name
        urlpatterns = [
            path('list/', self.wrapper(self.changelist_views), name='%s_%s_changelist' % info),
            path('add/', self.wrapper(self.add_views), name='%s_%s_add' % info),
            re_path('(?P<pk>\d+)/delete/', self.wrapper(self.delete_views), name='%s_%s_delete' % info),
            re_path('(?P<pk>\d+)/change/', self.wrapper(self.change_views), name='%s_%s_change' % info),
        ]
        extra = self.extra_urls()
        if extra:
            urlpatterns.extend(extra)

        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), None, None

    def wrapper(self, func, *args, **kwargs):
        @functools.wraps(func)
        def inner(request, *args, **kwargs):
            self.request = request
            return func(request, *args, **kwargs)

        return inner


class StarkAdminSite(object):

    def __init__(self):
        self._registry = {}
        self.app_name = 'stark'
        self.namespace = 'stark'

    def register(self, model_cls, stark_config_cls=None):
        if not stark_config_cls:
            stark_config_cls = StarkModelConfig
        self._registry[model_cls] = stark_config_cls(model_cls, self)

        # for k, v in self._registry.items():
        #     print(k, v)

    def get_urls(self):
        urlpatterns = []
        for model_cls, config_cls in self._registry.items():
            app_label = model_cls._meta.app_label
            model_name = model_cls._meta.model_name
            urlpatterns.append(path('%s/%s/' % (app_label, model_name), config_cls.urls))
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.namespace


site = StarkAdminSite()
