from django.conf.urls import url
from . import views


urlpatterns = [
    url('total_stock', views.TotalStockView.as_view(), name='total_stock'),
]