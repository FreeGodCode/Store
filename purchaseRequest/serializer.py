from rest_framework import serializers
from . import models


class PurchaseRequestSerializer(serializers.ModelSerializer):
    org_name = serializers.CharField(source='organization.org_name')
    area_name = serializers.CharField(source='organization.area_name')

    class Meta:
        model = models.PurchaseRequest
        fields = (
            'id', 'prq_identify', 'org_name', 'area_name', 'prq_type', 'prq_department', 'prq_date', 'prq_remarks',
            'prq_status', 'prq_creator', 'prq_creator_identify', 'prq_created_at', 'prq_closer', 'prq_closed_at',
            'prq_closeReason'
        )


class PurchaseRequestDetailSerializer(serializers.ModelSerializer):
    # org_name = serializers.CharField(source='purchase_request.organization.org_name')
    prq_identify = serializers.CharField(source='purchase_request.prq_identify')
    prqd_identify = serializers.CharField(source='material.material_identify')
    prqd_name = serializers.CharField(source='material.material_name')
    prqd_specification = serializers.CharField(source='material.material_specification')
    prqd_model = serializers.CharField(source='material.material_model')
    prqd_measure = serializers.CharField(source='material.measure_name')

    class Meta:
        model = models.PurchaseRequestDetail
        fields = (
            'id', 'prqd_identify','prq_identify', 'prqd_name', 'prqd_specification', 'prqd_model', 'prqd_measure','prqd_num',
            'prqd_present_num', 'prqd_remarks', 'prqd_used'
        )


class PurchaseRequestDetail2Serializer(serializers.ModelSerializer):
    prq_identify = serializers.CharField(source='purchase_request.prq_identify')
    prq_date = serializers.DateTimeField(source='purchase_request.prq_type')
    prq_department = serializers.CharField(source='purchase_request.prq_department')
    prq_creator = serializers.CharField(source='purchase_request.prq_creator')
    prq_creator_identify = serializers.CharField(source='purchase_request.prq_creator_identify')
    prqd_identify = serializers.CharField(source='material.material_identify')
    prqd_name = serializers.CharField(source='material.material_name')
    prqd_specification = serializers.CharField(source='material.material_specification')
    prqd_model = serializers.CharField(source='material.material_model')
    prqd_measure = serializers.CharField(source='material.measure_name')

    class Meta:
        model = models.PurchaseRequestDetail
        fields = (
            'id', 'prq_identify', 'prq_date', 'prq_department', 'prq_creator', 'prq_creator_identify','prqd_identify',
            'prqd_name', 'prqd_specification', 'prqd_model', 'prqd_measure','prqd_num', 'prqd_present_num', 'prqd_remarks'
        )
