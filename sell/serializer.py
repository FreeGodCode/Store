from rest_framework import serializers
from . import models


class SellOrderSerializer(serializers.ModelSerializer):
    org_name = serializers.CharField(source='organization.org_name')
    area_name = serializers.CharField(source='organization.area_name')
    customer_identify = serializers.CharField(source='customer.customer_identify')
    customer_name = serializers.CharField(source='customer.customer_name')

    class Meta:
        model = models.SellOrder
        fields = (
            'id', 'so_identify', 'org_name', 'area_name', 'so_type', 'customer_identify', 'customer_name',
            'so_date', 'deliver_ware_house', 'so_remarks', 'so_status',
            'so_creator', 'so_creator_identify', 'so_created_at'
        )


class SellOrderDetailSerializer(serializers.ModelSerializer):
    so_identify = serializers.CharField(source='sell_order.so_identify')
    sod_identify = serializers.CharField(source='material.material_identify')
    sod_name = serializers.CharField(source='material.material_name')
    sod_specification = serializers.CharField(source='material.material_specification')
    sod_model = serializers.CharField(source='material.material_model')
    sod_measure = serializers.CharField(source='material_measure_name')

    class Meta:
        model = models.SellOrderDetail
        fields = (
            'id', 'so_identify', 'sod_identify', 'sod_name', 'sod_specification', 'sod_model',
            'sod_measure', 'sod_num', 'sod_taxRate', 'sod_tax_unitPrice', 'sod_unitPrice',
            'sod_tax_sum', 'sod_sum', 'sod_tax_price', 'sod_remarks'
        )
