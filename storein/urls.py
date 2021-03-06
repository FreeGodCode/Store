# -*- coding: utf-8 -*-
# @Author:  ty
# @FileName: urls.py
# @Time:  2021/3/4 下午9:17
# @Description:
from django.conf.urls import url
from . import views

urlpatterns = [
    url('purchase_receipts', views.PurchaseReceiptsView.as_view(), name='purchase_receipts'),
    url('purchase_receipt_new', views.PurchaseReceiptNewView.as_view(), name='purchase_receipt_new'),
    url('purchase_receipt_update', views.PurchaseReceiptUpdateView.as_view(), name='purchase_receipt_update'),
    url('purchase_order_choice', views.PurchaseOrderChoiceView.as_view(), name='purchase_order_choice'),
    url('purchase_receipt_detail_save', views.PurchaseReceiptDetailSaveView.as_view(), name='purchase_receipt_detail_save'),
    url('purchase_receipt_detail_submit', views.PurchaseReceiptDetailSubmitView.as_view(), name='purchase_receipt_detail_submit'),
    url('purchase_receipt_delete', views.PurchaseReceiptDeleteView.as_view(), name='purchase_receipt_delete')
]