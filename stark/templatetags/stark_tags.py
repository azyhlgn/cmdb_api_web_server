from django.template import Library
from types import FunctionType

register = Library()


def head_list(vo):
    if vo.list_display:
        for item in vo.list_display:
            if isinstance(item, FunctionType):
                yield item(vo.config, header=True)
            else:
                yield vo.config.model_cls._meta.get_field(item).verbose_name
    else:
        yield from [field.verbose_name for field in vo.config.model_cls._meta.fields]


def data_list(vo):
    if vo.list_display:
        for obj in vo.queryset:
            data_row = []
            for field in vo.list_display:
                # 判断是否是函数
                if isinstance(field, FunctionType):
                    data_row.append(field(vo.config, row=obj))
                else:
                    # 处理显示choices字段
                    if vo.config.model_cls._meta.get_field(field).choices:
                        data_row.append(getattr(obj, 'get_%s_display' % field))
                    else:
                        data_row.append(getattr(obj, field))
            yield data_row
    else:
        for obj in vo.queryset:
            data_row = []
            for field in vo.config.model_cls._meta.fields:
                if field.choices:
                    data_row.append(getattr(obj, 'get_%s_display' % field.name))
                else:
                    data_row.append(getattr(obj, field.name))
            yield data_row


@register.inclusion_tag('stark/table.html')
def table(vo):
    # # 处理需要显示的字段
    # if vo.list_display:
    #     # 根据list_display得到需要显示的字段的verbose_name
    #     head_list = []
    #     for item in vo.list_display:
    #         if isinstance(item, FunctionType):
    #             head_list.append(item(vo.config, header=True))
    #         else:
    #             head_list.append(vo.config.model_cls._meta.get_field(item).verbose_name)
    #     data_list = []
    #     for obj in vo.queryset:
    #         data_row = []
    #         for item in vo.list_display:
    #             if isinstance(item, FunctionType):
    #                 data_row.append(item(vo.config, row=obj))
    #             else:
    #                 data_row.append(getattr(obj, item))
    #         data_list.append(data_row)
    # # 如果没有定义list_display字段 则显示全部
    # else:
    #     head_list = [field.verbose_name for field in vo.config.model_cls._meta.fields]
    #     data_list = []
    #     for obj in vo.queryset:
    #         data_row = []
    #         for field in vo.config.model_cls._meta.fields:
    #             data_row.append(getattr(obj, field.name))
    #         data_list.append(data_row)
    return {'head_list': head_list(vo), 'data_list': data_list(vo)}
