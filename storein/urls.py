# -*- coding: utf-8 -*-
# @Author:  ty
# @FileName: urls.py
# @Time:  2021/3/4 下午9:17
# @Description:
from django.conf.urls import url
from . import views

urlpatterns = [
    url('buy_in_stores', views.BuyInStoresView.as_view(), name='buy_in_stores'),
    url('buy_in_store_new', views.BuyInStoreNewView.as_view(), name='buy_in_store_new'),
    url('buy_in_store_update', views.BuyInStoreUpdateView.as_view(), name='buy_in_store_update'),
    url('pOChoice', views.POChoiceView.as_view(), name='pOChoice'),
    url('buy_in_store_detail_save', views.BuyInStoreDetailSaveView.as_view(), name='buy_in_store_detail_save'),
    url('buy_in_store_detail_submit', views.BuyInStoreDetailSubmitView.as_view(), name='buy_in_store_detail_submit'),
    url('buy_in_store_delete', views.BuyInStoreDeleteView.as_view(), name='buy_in_store_delete')
]