import json

from repository import models


# 用于将内存 硬盘 网卡数据入库
class Saver(object):

    def save(self, server, data, model_name, search_name):
        # server 用于搜索 和在创建作为外键传入
        # model_name 为了反射实现工厂模式 兼容三种保存
        # search_name 为了在数据库查询时 作为拟造查询条件传入 用于兼容 slot_in 和 name_in 两种查询
        print('进入save')
        print(json.dumps(data))
        model = getattr(models, model_name)
        old_data = model.objects.filter(server=server.first())
        new_data_set = set(data.keys())
        old_data_set = set(old_data.values_list(search_name, flat=True))

        # 用于资产变更表的创建
        asset_change_log = {}
        # 资产变更表中需要有的字段
        asset_change_fields = model._meta.get_fields()
        asset_change_fields = {field.name: field.verbose_name for field in asset_change_fields if
                               field.name not in ('id', 'server')}
        print(asset_change_fields.items())

        # 更新已存在的
        update_data_set = new_data_set & old_data_set
        if len(update_data_set) > 0:
            add_model_obj_list = []
            update_fields = []
            # 记录资产变更
            update_content_dict = {}
            # 用于兼容使用slot和name查询的情况
            update_search_dict = {search_name + '__in': update_data_set}
            for item in old_data.filter(**update_search_dict):
                update_obj_dict = {}
                updated_flag = False

                for key, value in data[getattr(item, search_name)].items():
                    old_value = getattr(item, key)
                    if str(value) == str(old_value):
                        pass
                    else:
                        setattr(item, key, value)
                        update_fields.append(key)
                        updated_flag = True

                        # 增加更新资产的记录
                        update_obj_dict[asset_change_fields[key]] = str(old_value) + ' --> ' + str(value)
                if updated_flag:
                    add_model_obj_list.append(item)
                    update_content_dict[getattr(item, search_name)] = update_obj_dict
            if len(add_model_obj_list) > 0:
                model.objects.bulk_update(add_model_obj_list, update_fields)
                asset_change_log['更新'] = update_content_dict

        # 删除新数据中没有的
        delete_data_set = old_data_set - new_data_set
        if len(delete_data_set) > 0:
            delete_search_dict = {search_name + '__in': delete_data_set}
            old_data.filter(**delete_search_dict).delete()
            asset_change_log['删除'] = delete_data_set

        # 新增老数据中没有的
        add_data_set = new_data_set - old_data_set
        if len(add_data_set) > 0:
            add_model_obj_list = []
            # 用于记录资产变更信息的字典
            add_content_dict = {}
            for index in add_data_set:
                obj = model(**data[index], server=server.first())
                # 用于记录单个资产变更的字典
                add_obj_dict = {}
                for key, value in asset_change_fields.items():
                    add_obj_dict[key] = getattr(obj, key)

                add_content_dict[index] = add_obj_dict
                add_model_obj_list.append(obj)
            model.objects.bulk_create(add_model_obj_list)
            asset_change_log['新增'] = add_content_dict

        print(asset_change_log)
        if len(asset_change_log) > 0:
            models.Asset.objects.create(server=server.first(), content=asset_change_log)


my_saver = Saver()
