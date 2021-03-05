from django.conf.urls import url
from . import views


urlpatterns = [
    url('purchase_requests', views.PurchaseRequestsView.as_view  , name='purchase_requests'),
    url('purchase_request_new', views.PurchaseRequestNewView.as_view  , name='purchase_request_new'),
    url('purchase_request_update', views.PurchaseRequestUpdateView.as_view  , name='purchase_request_update'),
    url('purchase_request_detail_save', views.PurchaseRequestDetailSaveView.as_view  , name='purchase_request_detail_save'),
    url('purchase_request_detail_submit', views.PurchaseRequestDetailSubmitView.as_view  , name='purchase_request_detail_submit'),
    url('purchase_request_detail_new', views.PurchaseRequestDetailNewView.as_view  , name='purchase_request_detail_new'),
    url('purchase_request_delete', views.PurchaseRequestDeleteView.as_view  , name='purchase_request_delete'),
    url('purchase_request_close', views.PurchaseRequestCloseView.as_view  , name='purchase_request_close'),
]