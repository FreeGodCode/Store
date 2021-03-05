from rest_framework import serializers
from . import models


class PurchaseRequestSerializer(serializers.ModelSerializer):
    org_name = serializers.CharField(source='organization.org_name')
    area_name = serializers.CharField(source='organization.area_name')

    class Meta:
        model = models.PurchaseRequest
        fields = (
            'id', 'pr_identify', 'org_name', 'area_name', 'pr_type', 'pr_department', 'pr_date', 'pr_remarks',
            'pr_status', 'pr_creator', 'pr_creator_identify', 'pr_created_at', 'pr_closer', 'pr_closed_at',
            'pr_closeReason'
        )


class PurchaseRequestDetailSerializer(serializers.ModelSerializer):
    # org_name = serializers.CharField(source='purchase_request.organization.org_name')
    pr_identify = serializers.CharField(source='purchase_request.pr_identify')
    prd_identify = serializers.CharField(source='material.material_identify')
    prd_name = serializers.CharField(source='material.material_name')
    prd_specification = serializers.CharField(source='material.material_specification')
    prd_model = serializers.CharField(source='material.material_model')
    prd_measure = serializers.CharField(source='material.measure_name')

    class Meta:
        model = models.PurchaseRequestDetail
        fields = (
            'id', 'prd_identify','pr_identify', 'prd_name', 'prd_specification', 'prd_model', 'prd_measure','prd_num',
            'prd_present_num', 'prd_remarks', 'prd_used'
        )


class PurchaseRequestDetail2Serializer(serializers.ModelSerializer):
    pr_identify = serializers.CharField(source='purchase_request.pr_identify')
    pr_date = serializers.DateTimeField(source='purchase_request.pr_type')
    pr_department = serializers.CharField(source='purchase_request.pr_department')
    pr_creator = serializers.CharField(source='purchase_request.pr_creator')
    pr_creator_identify = serializers.CharField(source='purchase_request.pr_creator_identify')
    prd_identify = serializers.CharField(source='material.material_identify')
    prd_name = serializers.CharField(source='material.material_name')
    prd_specification = serializers.CharField(source='material.material_specification')
    prd_model = serializers.CharField(source='material.material_model')
    prd_measure = serializers.CharField(source='material.measure_name')

    class Meta:
        model = models.PurchaseRequestDetail
        fields = (
            'id', 'pr_identify', 'pr_date', 'pr_department', 'pr_creator', 'pr_creator_identify','prd_identify',
            'prd_name', 'prd_specification', 'prd_model', 'prd_measure','prd_num', 'prd_present_num', 'prd_remarks'
        )
