from repository import models


# 用于将内存 硬盘 网卡数据入库
class Saver(object):

    def save(self, server, data, model_name, search_name):
        # server 用于搜索 和在创建作为外键传入
        # model_name 为了反射实现工厂模式 兼容三种保存
        # search_name 为了在数据库查询时 作为拟造查询条件传入 用于兼容 slot_in 和 name_in 两种查询
        print('进入dms')
        model = getattr(models, model_name)
        old_data = model.objects.filter(server=server.first())
        new_data_set = set(data.keys())
        print(new_data_set)
        old_data_set = set(old_data.values_list(search_name, flat=True))
        print(old_data_set)

        # 更新已存在的
        update_data_set = new_data_set & old_data_set
        if len(update_data_set) > 0:
            add_model_obj_list = []
            update_fields = []
            # 用于兼容使用slot和name查询的情况
            update_search_dict = {search_name + '__in': update_data_set}
            for item in old_data.filter(**update_search_dict):
                for key, value in data[getattr(item, search_name)].items():
                    setattr(item, key, value)
                    add_model_obj_list.append(item)
                    update_fields.append(key)
            model.objects.bulk_update(add_model_obj_list, update_fields)
            print('更新', update_data_set)

        # 删除新数据中没有的
        delete_data_set = old_data_set - new_data_set
        if len(delete_data_set) > 0:
            delete_search_dict = {search_name + '__in': delete_data_set}
            print('删除', delete_data_set)
            old_data.filter(**delete_search_dict).delete()

        # 新增老数据中没有的
        add_data_set = new_data_set - old_data_set
        if len(add_data_set) > 0:
            add_model_obj_list = []
            for index in add_data_set:

                add_model_obj_list.append(model(**data[index], server=server.first()))
            model.objects.bulk_create(add_model_obj_list)
            print('新增', add_data_set)


my_saver = Saver()
