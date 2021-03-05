# -*- coding: utf-8 -*-
# @Author:  ty
# @FileName: serializer.py
# @Time:  2021/3/4 下午11:56
# @Description:
from rest_framework import serializers
from . import models


class PurchaseContractSerializer(serializers.ModelSerializer):
    """采购合同序列化器"""
    org_name = serializers.CharField(source='organization.org_name')
    area_name = serializers.CharField(source='organization.area_name')
    supply_name = serializers.CharField(source='supplier.supply_name')
    supply_identify = serializers.CharField(source='supplier.supply_identify')

    class Meta:
        model = models.PurchaseContract
        fields = (
            'id', 'pc_identify', 'org_name', 'area_name', 'pc_name', 'supply_name', 'supply_identify', 'pc_date',
            'pc_sum', 'pc_remarks', 'pc_status', 'pc_creator', 'pc_creator_identify', 'pc_createDate'
        )


class PurchaseContractDetailSerializer(serializers.ModelSerializer):
    """采购合同详情"""
    pc_identify = serializers.CharField(source='purchase_contract.pc_identify')
    cd_identify = serializers.CharField(source='material.material_identify')
    cd_name = serializers.CharField(source='material.material_name')
    cd_specification = serializers.CharField(source='material.material_specification')
    cd_model = serializers.CharField(source='material.material_model')
    cd_measure = serializers.CharField(source='material.measure_name')

    class Meta:
        model = models.PurchaseContractDetail
        fields = (
            'id', 'cd_identify', 'pc_identify', 'cd_name', 'cd_specification',  'cd_model', 'cd_measure', 'cd_num',
            'cd_taxRate', 'cd_tax_unitPrice', 'cd_unitPrice', 'cd_tax_sum', 'cd_sum', 'cd_tax_price', 'cd_pr_identify',
            'cd_prd_remarks'
        )


class PurchaseContractPayDetailSerializer(serializers.ModelSerializer):
    """采购合同付款详情"""
    pc_identify = serializers.CharField(source='purchase_contract.pc_identify')

    class Meta:
        model = models.PurchaseContractPayDetail
        fields = (
            'id', 'pc_identify', 'pay_batch', 'pay_rate', 'pay_price', 'pay_planDate', 'pay_prepay', 'pay_remarks'
        )


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """采购订单"""
    org_name = serializers.CharField(source='organization.org_name')
    area_name = serializers.CharField(source='organization.area_name')
    supply_name = serializers.CharField(source='supplier.supply_name')
    supply_identify = serializers.CharField(source='supplier.supply_identify')

    class Meta:
        model = models.PurchaseOrder
        fields = (
            'id', 'po_identify', 'po_serial', 'org_name', 'area_name', 'supply_name', 'supply_identify', 'po_date',
            'po_sum', 'po_remarks', 'pc_identify', 'po_status', 'po_creator', 'po_creator_identify', 'po_createDate'
        )


class OrderDetailSerializer(serializers.ModelSerializer):
    """订单详情"""
    po_identify = serializers.CharField(source='purchase_order.po_identify')
    po_date = serializers.DateTimeField(source='purchase_order.po_date')
    od_identify = serializers.CharField(source='material.material_identify')
    od_name = serializers.CharField(source='material.material_name')
    od_specification = serializers.CharField(source='material.material_specification')
    od_model = serializers.CharField(source='material.material_model')
    od_measure = serializers.CharField(source='material.measure_name')

    class Meta:
        model = models.OrderDetail
        fields = (
            'id', 'po_identify', 'po_date', 'od_identify', 'od_name', 'od_specification',  'od_model', 'od_measure',
            'od_num', 'od_taxRate', 'od_tax_unitPrice', 'od_unitPrice', 'od_tax_sum', 'od_sum', 'od_tax_price',
            'od_pr_identify', 'od_prd_remarks'
        )


class OrderDetailToBuyInStoreDetailSerializer(serializers.ModelSerializer):
    """采购订单转化为入库订单详情"""
    po_identify = serializers.CharField(source='purchase_order.po_identify')
    po_date = serializers.DateTimeField(source='purchase_order.po_date')
    pr_identify = serializers.CharField(source='od_pr_identify')
    bd_identify = serializers.CharField(source='material.material_identify')
    bd_name = serializers.CharField(source='material.material_name')
    bd_specification = serializers.CharField(source='material.material_specification')
    bd_model = serializers.CharField(source='material.material_model')
    bd_measure = serializers.CharField(source='material.measure_name')
    bd_unitPrice = serializers.DecimalField(max_digits=10, decimal_places=2, source='od_unitPrice')
    bd_paper_num = serializers.IntegerField(source='od_num')

    class Meta:
        model = models.OrderDetail
        fields = (
            'id', 'po_identify', 'pr_identify', 'po_date', 'bd_identify', 'bd_name', 'bd_specification', 'bd_model',
            'bd_measure', 'bd_paper_num', 'bd_unitPrice'
        )