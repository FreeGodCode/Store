# -*- coding: utf-8 -*-
# @Author:  ty
# @FileName: urls.py
# @Time:  2021/3/4 下午9:17
# @Description:
from django.conf.urls import url
from . import views

patterns = [
    url(r'^', views.LoginView.as_view(), name=''),
]