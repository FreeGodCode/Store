from rest_framework import serializers
from . import models


class TransferRequestSerializer(serializers.ModelSerializer):
    org_name = serializers.CharField(source='organization.org_name')

    class Meta:
        model = models.TransferRequest
        fields = (
            'id', 'str_identify', 'org_name', 'str_to_house', 'str_from_house', 'str_date', 'str_department',
            'str_status','str_creator', 'str_creator_identify', 'str_created_at'
        )


class TransferRequestDetailSerializer(serializers.ModelSerializer):
    str_identify = serializers.CharField(source='transfer_request.str_identify')
    trd_identify = serializers.CharField(source='material.material_identify')
    trd_name = serializers.CharField(source='material.material_name')
    trd_specification = serializers.CharField(source='material.material_specification')
    trd_model = serializers.CharField(source='material.material_model')
    trd_measure = serializers.CharField(source='material.measure_name')

    class Meta:
        model = models.TransferRequestDetail
        fields = (
            'id', 'str_identify', 'trd_identify', 'trd_name', 'trd_specification', 'trd_model', 'trd_measure',
            'trd_num', 'trd_present_num', 'trd_used', 'trd_remarks'
        )


class TransferRequestDetailToTransferDetailSerializer(serializers.ModelSerializer):
    str_identify = serializers.CharField(source='transfer_request.str_identify')
    td_identify = serializers.CharField(source='material.material_identify')
    td_name = serializers.CharField(source='material.material_name')
    td_specification = serializers.CharField(source='material.material_specification')
    td_model = serializers.CharField(source='material.material_model')
    td_measure = serializers.CharField(source='material.measure_name')
    td_apply_num = serializers.CharField(source='trd_num')

    class Meta:
        model = models.TransferRequestDetail
        fields = (
            'id', 'str_identify', 'td_identify', 'td_name', 'td_specification', 'td_model', 'td_measure', 'td_apply_num'
        )


class TransferSerializer(serializers.ModelSerializer):
    org_name = serializers.CharField(source='organization.org_name')

    class Meta:
        model = models.Transfer
        fields = (
            'id', 'st_identify', 'org_name', 'st_to_house', 'st_from_house', 'st_date', 'st_status', 'st_creator',
            'st_creator_identify', 'st_created_at'
        )


class TransferDetailSerializer(serializers.ModelSerializer):
    st_identify = serializers.CharField(source='transfer.st_identify')
    td_identify = serializers.CharField(source='material.material_identify')
    td_name = serializers.CharField(source='material.material_name')
    td_specification = serializers.CharField(source='material.material_specification')
    td_model = serializers.CharField(source='material.material_model')
    td_measure = serializers.CharField(source='material.measure_name')

    class Meta:
        model = models.TransferDetail
        fields = (
            'id', 'str_identify', 'st_identify', 'td_identify', 'td_name', 'td_specification', 'td_model', 'td_measure',
            'td_apply_num', 'td_real_num ', 'td_present_num', 'td_remarks'
        )