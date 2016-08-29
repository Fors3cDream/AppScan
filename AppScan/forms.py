#coding=utf-8

from django import forms
from models import User

class UploadFileForm(forms.Form):
	file = forms.FileField()

class UserForm(forms.Form):
    username = forms.CharField(label = u'用户名', max_length = 100)
    password = forms.CharField(label = u'密  码', widget = forms.PasswordInput())