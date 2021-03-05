from django.conf.urls import url
from . import views


urlpatterns = [
    url('transfer_requests', views.TransferRequestsView.as_view(), name='transfer_requests'),
    url('transfer_request_new', views.TransferRequestNewView.as_view(), name='transfer_request_new'),
    url('transfer_request_update', views.TransferRequestUpdateView.as_view(), name='transfer_request_update'),
    url('transfer_request_detail_save', views.TransferRequestDetailSaveView.as_view(), name='transfer_request_detail_save'),
    url('transfer_request_detail_submit', views.TransferRequestDetailNewView.as_view(), name='transfer_request_detail_submit'),
    url('transfer_request_delete', views.TransfersView.as_view(), name='transfer_request_delete'),
    url('transfer_new', views.TransferNewView.as_view(), name='transfer_new'),
    url('transfer_request_detail_new_by_transfer_request', views.TransferRequestDetailNewByTrView.as_view(), name='transfer_request_detail_new_by_transfer_request'),
    url('trd_new', views.TrdNewView.as_view(), name='trd_new'),
    url('transfer_update', views.TransferUpdateView.as_view(), name='transfer_update'),
    url('transfer_detail_save', views.TransferDetailSaveView.as_view(), name='transfer_detail_save'),
    url('transfer_delete', views.TransferDeleteView.as_view(), name='transfer_delete'),
]