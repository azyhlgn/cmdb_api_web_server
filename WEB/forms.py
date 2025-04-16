from django import forms

from repository import models


class BaseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class BusinessUnitForm(BaseForm):
    class Meta:
        model = models.BusinessUnit
        fields = '__all__'


class ServerForm(BaseForm):
    class Meta:
        model = models.Server
        fields = '__all__'
