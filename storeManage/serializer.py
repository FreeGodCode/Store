from rest_framework import serializers
from . import models


class TotalStockSerializer(serializers.ModelSerializer):
    total_identify = serializers.CharField(source='totalwarehouse.total_identify')
    total_name = serializers.CharField(source='totalwarehouse.total_name')
    org_identify = serializers.CharField(source='totalwarehouse.organization.org_identify')
    org_name = serializers.CharField(source='totalwarehouse.organization.org_name')
    material_identify = serializers.CharField(source='material.material_identify')
    material_name = serializers.CharField(source='material.material_name')
    material_specification = serializers.CharField(source='material.material_specification')
    material_model = serializers.CharField(source='material.material_model')
    material_measure = serializers.CharField(source='material.measure_name')

    class Meta:
        model = models.TotalStock
        fields = (
            'id', 'total_identify', 'total_name', 'org_identify', 'org_name', 'material_identify', 'material_name',
            'material_specification', 'material_model', 'material_measure', 'ts_present_num', 'ts_present_price',
            'ts_present_sum'
        )


class TotalStockToTrSerializer(serializers.ModelSerializer):
    trd_identify = serializers.CharField(source='material.material_identify')
    trd_name = serializers.CharField(source='material.material_name')
    trd_specification = serializers.CharField(source='material.material_specification')
    trd_model = serializers.CharField(source='material.material_model')
    trd_measure = serializers.CharField(source='material.measure_name')
    trd_present_num = serializers.IntegerField(source='ts_present_num')

    class Meta:
        model = models.TotalStock
        fields = (
            'id', 'trd_identify', 'trd_name', 'trd_specification', 'trd_model', 'trd_measure', 'trd_present_num'
        )


class TotalStockToTdSerializer(serializers.ModelSerializer):
    td_identify = serializers.CharField(source='material.material_identify')
    td_name = serializers.CharField(source='material.material_name')
    td_specification = serializers.CharField(source='material.material_specification')
    td_model = serializers.CharField(source='material.material_model')
    td_measure = serializers.CharField(source='material.measure_name')
    td_present_num = serializers.IntegerField(source='ts_present_num')

    class Meta:
        model = models.TotalStock
        fields = (
            'id', 'td_identify', 'td_name', 'td_specification', 'td_model', 'td_measure', 'td_present_num'
        )