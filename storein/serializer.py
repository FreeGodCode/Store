# -*- coding: utf-8 -*-
# @Author:  ty
# @FileName: serializer.py
# @Time:  2021/3/4 下午9:18
# @Description:
from rest_framework import serializers
from . import models


class PurchaseReceiptSerializer(serializers.ModelSerializer):
    org_name = serializers.CharField(source='organization.org_name')
    area_name = serializers.CharField(source='organization.area_name')
    total_name = serializers.CharField(source='total_ware_house.total_name')
    supply_name = serializers.CharField(source='supplier.supply_name')
    supply_identify = serializers.CharField(source='supplier.supply_identify')
    # total_name = serializers.CharField(source='totalwarehouse.total_name')

    class Meta:
        model = models.PurchaseReceipt
        fields = (
            'id', 'org_name', 'area_name', 'total_name', 'supply_name', 'supply_identify', 'prc_identify', 'prc_date',
            'prc_remarks', 'prc_status', 'prc_creator', 'prc_creator_identify', 'prc_created_at'
        )


class PurchaseReceiptDetailSerializer(serializers.ModelSerializer):
    prc_identify = serializers.CharField(source='purchase_receipt.prc_identify')
    prcd_identify = serializers.CharField(source='material.material_identify')
    prcd_name = serializers.CharField(source='material.material_name')
    prcd_specification = serializers.CharField(source='material.material_specification')
    prcd_model = serializers.CharField(source='material.material_model')
    prcd_measure = serializers.CharField(source='material.measure_name')

    class Meta:
        model = models.PurchaseReceiptDetail
        fields = (
            'id', 'prc_identify', 'prcd_identify', 'prcd_name', 'prcd_specification', 'prcd_model', 'prcd_measure', 'prcd_paper_num',
            'prcd_real_num', 'prcd_unitPrice', 'prcd_sum', 'po_identify', 'prq_identify'
        )