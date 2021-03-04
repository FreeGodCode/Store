# -*- coding: utf-8 -*-
# @Author:  ty
# @FileName: serializer.py
# @Time:  2021/3/4 下午9:18
# @Description:
from rest_framework import serializers
from .models import BuyInStore, BuyInStoreDetail


class BuyInStoreSerializer(serializers.ModelSerializer):
    org_name = serializers.CharField(source='organization.org_name')
    area_name = serializers.CharField(source='organization.area_name')
    total_name = serializers.CharField(source='total_ware_house.total_name')
    supply_name = serializers.CharField(source='supplier.supply_name')
    supply_identify = serializers.CharField(source='supplier.supply_identify')
    # total_name = serializers.CharField(source='totalwarehouse.total_name')

    class Meta:
        model = BuyInStore
        fields = (
            'id', 'org_name', 'area_name', 'total_name', 'supply_name', 'supply_identify', 'bis_identify', 'bis_date', 'bis_remarks', 'bis_status', 'bis_creator', 'bis_creator_identify', 'bis_created_at'
        )


class BuyInStoreDetailSerializer(serializers.ModelSerializer):
    bis_identify = serializers.CharField(source='buy_in_store.bis_identify')
    bd_identify = serializers.CharField(source='material.material_identify')
    bd_name = serializers.CharField(source='material.material_name')
    bd_specification = serializers.CharField(source='material.material_specification')
    bd_model = serializers.CharField(source='material.material_model')
    bd_measure = serializers.CharField(source='material.measure_name')

    class Meta:
        model = BuyInStoreDetail
        fields = (
            'id', 'bis_identify', 'bd_identify', 'bd_name', 'bd_specification', 'bd_model', 'bd_measure', 'bd_paper_num', 'bd_real_num', 'bd_unitPrice', 'bd_sum', 'po_identify', 'pr_identify'
        )