from repository import models


def get_name_value_form_field(asset_qs, asset_model_name,title):
    model_cls = getattr(models, asset_model_name)
    field_name_list = [field.name for field in model_cls._meta.fields]

    value_list = []
    for asset in asset_qs:
        row_data = []
        for name in field_name_list:
            row_data.append(getattr(asset, name))
        value_list.append(row_data)

    result = {
        'title':title,
        'name': field_name_list,
        'value': value_list,
    }
    return result
