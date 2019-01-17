from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

class UserCreateForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['username','email','password1','password2']

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for visible in self.visible_fields():
            visible.label = ''
            visible.field.widget.attrs['placeholder'] = visible.name
            visible.field.widget.attrs['class'] = 'form-control'
