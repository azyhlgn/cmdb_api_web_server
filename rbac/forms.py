from django import forms

from rbac.models import Permission


class PermissionForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PermissionForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.label == '所属二级菜单':
                choices_list = list(Permission.objects.filter(('is_changelist', True)).values_list('id', 'title'))
                choices_list.insert(0, ('', '--------'))
                field.choices = choices_list
            if field.label == 'Url标题':
                field.required = True
            field.widget.attrs['class'] = 'form-control'
