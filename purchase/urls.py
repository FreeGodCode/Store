# -*- coding: utf-8 -*-
# @Author:  ty
# @FileName: urls.py
# @Time:  2021/3/4 下午11:56
# @Description:
from django.conf.urls import url
from . import views

urlpatterns = [
    url('purchase_contracts', views.PurchaseContractsView.as_view(), name='purchase_contracts'),
    url('purchase_contract_new', views.PurchaseContractNewView.as_view(), name='purchase_contract_new'),
    url('purchase_contract_update', views.PurchaseContractUpdateView.as_view(), name='purchase_contract_update'),
    url('purchase_contract_detail_save', views.PurchaseContractDetailSaveView.as_view(), name='purchase_contract_detail_save'),
    url('purchase_contract_detail_submit', views.PurchaseContractDetailSubmitView.as_view(), name='purchase_contract_detail_submit'),
    url('purchase_contract_detail_new', views.PurchaseContractDetailNewView.as_view(), name='purchase_contract_detail_new'),
    url('purchase_contract_delete', views.PurchaseContractDeleteView.as_view(), name='purchase_contract_delete'),

    url('purchase_orders', views.PurchaseOrdersView.as_view(), name='purchase_orders'),
    url('purchase_order_new', views.PurchaseOrderNewView.as_view(), name='purchase_order_new'),
    url('prChoice', views.PrChoiceView.as_view(), name='prChoice'),
    # url('purchase_order_newByPurchaseContract', views.PurchaseOrderNewByPurchaseContractView.as_view(), name='purchase_order_newByPurchaseContract'),
    url('purchase_contract_choice', views.PurchaseContractChoiceView.as_view(), name='purchase_contract_choice'),
    url('purchase_order_update', views.PurchaseOrderUpdateView.as_view(), name='purchase_order_update'),
    url('purchase_order_save', views.PurchaseOrderSaveView.as_view(), name='purchase_order_save'),
    url('purchase_order_submit', views.PurchaseOrderSubmitView.as_view(), name='purchase_order_submit'),
    url('purchase_order_delete', views.PurchaseOrderDeleteView.as_view(), name='purchase_order_delete'),
]