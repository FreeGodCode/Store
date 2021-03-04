# -*- coding: utf-8 -*-
# @Author:  ty
# @FileName: serializer.py
# @Time:  2021/3/4 下午1:38
# @Description:
from rest_framework import serializers
from . import models


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Area
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        # fields = '__all__'
        # fields = ('user_id', 'user_name', 'user_phone_number', 'user_mailbox', 'user_departments', 'user_roles',
        #                 'user_status', 'user_creator', 'user_created_at', 'area_name')
        exclude = ('password', 'first_name', 'last_name')


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Role
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Department
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Customer
        fields = "__all__"


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Supplier
        fields = "__all__"


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Organization
        fields = "__all__"


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Brand
        fields = "__all__"


class TotalWareHouseSerializer(serializers.ModelSerializer):
    area_name = serializers.CharField(source='organization.area_name')
    org_name = serializers.CharField(source='organization.org_name')

    class Meta:
        model = models.TotalWareHouse
        fields = (
            'id', 'total_identify', 'total_name', 'area_name', 'org_name', 'total_status', 'total_belong_center',
            'total_belong_center_identify', 'brand_name', 'total_remarks', 'total_creator', 'total_createDate'
        )


class CenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Center
        fields = "__all__"


class CenterWareHouseSerializer(serializers.ModelSerializer):
    area_name = serializers.CharField(source='organization.area_name')
    org_name = serializers.CharField(source='organization.org_name')
    center_name = serializers.CharField(source='center.center_name')

    class Meta:
        model = models.CenterWareHouse
        fields = ('id', 'center_wh_identify', 'center_wh_name', 'area_name', 'org_name', 'center_name',
                  'brand_name', 'center_wh_status', 'center_wh_remarks', 'center_wh_creator', 'center_wh_createDate'
                  )


class MeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Measure
        fields = "__all__"


class MaterialTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MaterialType
        fields = "__all__"


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Material
        fields = "__all__"
