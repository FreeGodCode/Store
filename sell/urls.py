from django.conf.urls import url
from . import views


urlpatterns = [
    url('sell_orders', views.SellOrdersView.as_view(), name='sell_orders'),
    url('sell_order_new', views.SellOrderNewView.as_view(), name='sell_order_new'),
    url('sell_order_update', views.SellOrderUpdateView.as_view(), name='sell_order_update'),
    url('sell_order_detail_save', views.SellOrderDetailSaveView.as_view(), name='sell_order_detail_save'),
    url('sell_order_detail_submit', views.SellOrderDetailSubmitView.as_view(), name='sell_order_detail_submit'),
    url('sell_order_detail_new', views.SellOrderDetailNewView.as_view(), name='sell_order_detail_new'),
    url('sell_order_delete', views.SellOrderDeleteView.as_view(), name='sell_order_delete'),
]