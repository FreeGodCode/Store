# -*- coding: utf-8 -*-
# @Author:  ty
# @FileName: urls.py
# @Time:  2021/3/4 下午2:05
# @Description:
from django.conf.urls import url
from . import views


urlpatterns = [
    # user
    url('login', views.LoginView.as_view(), name='login'),
    url('login_exit', views.LoginExitView.as_view(), name='login_exit'),
    url('user', views.UserView.as_view(), name='user'),
    url('user_new', views.UserNewView.as_view(), name='user_new'),
    url('user_add', views.UserAddView.as_view(), name='user_add'),
    url('user_update', views.UserUpdateView.as_view(), name='user_update'),
    url('user_status', views.UserStatusView.as_view(), name='user_status'),
    url('users', views.UsersView.as_view(), name='users'),

    # area
    url('areas', views.AreasView.as_view(), name='areas'),

    # role
    url('roles', views.RolesView.as_view(), name='roles'),
    url('role_add', views.RoleAddView.as_view(), name='role_add'),
    url('role_update', views.RoleUpdateView.as_view(), name='role_update'),
    url('role_status', views.RoleStatusView.as_view(), name='role_status'),

    # department
    url('departments', views.DepartmentsView.as_view(), name='departments'),
    url('department_add', views.DepartmentAddView.as_view(), name='department_add'),
    url('department_update', views.DepartmentUpdateView.as_view(), name='department_update'),
    url('department_status', views.DepartmentStatusView.as_view(), name='department_status'),
    url('role_permission_add_save', views.RolePermissionAddSaveView.as_view(), name='role_permission_add_save'),

    # customer
    url('customers', views.CustomersView.as_view(), name='customers'),
    url('customer_add', views.CustomerAddView.as_view(), name='customer_add'),
    url('customer_update', views.CustomerUpdateView.as_view(), name='customer_update'),
    url('customer_status', views.CustomerStatusView.as_view(), name='customer_status'),

    # organization
    url('organizations', views.OrganizationsView.as_view(), name='organizations'),
    url('organization_new', views.OrganizationNewView.as_view(), name='organization_new'),
    url('organization_add', views.OrganizationAddView.as_view(), name='organization_add'),
    url('organization_update', views.OrganizationUpdateView.as_view(), name='organization_update'),
    url('organization_status', views.OrganizationStatusView.as_view(), name='organization_status'),

    # brand
    url('brands', views.BrandsView.as_view(), name='brands'),
    url('brand_add', views.BrandAddView.as_view(), name='brand_add'),
    url('brand_update', views.BrandUpdateView.as_view(), name='brand_update'),
    url('brand_status', views.BrandStatusView.as_view(), name='brand_status'),

    # total warehouse
    url('totalWareHouses', views.TotalWareHousesView.as_view(), name='totalWareHouses'),
    url('totalWareHouse_new', views.TotalWareHouseNewView.as_view(), name='totalWareHouse_new'),
    url('totalWareHouse_add', views.TotalWareHouseAddView.as_view(), name='totalWareHouse_add'),
    url('totalWareHouse_update', views.TotalWareHouseUpdateView.as_view(), name='totalWareHouse_update'),
    url('totalWareHouse_status', views.TotalWareHouseStatusView.as_view(), name='totalWareHouse_update'),

    # center
    url('centers', views.CentersView.as_view(), name='centers'),
    url('center_new', views.CenterNewView.as_view(), name='center_new'),
    url('center_add', views.CenterAddView.as_view(), name='center_add'),
    url('center_update', views.CenterUpdateView.as_view(), name='center_update'),
    url('center_status', views.CenterStatusView.as_view(), name='center_status'),

    # center warehouse
    # url('centerWareHouses', views.CenterWareHousesView.as_view(), name='centerWareHouses'),
    # url('centerWareHouse_new', views.CenterWareHouseNewView.as_view(), name='centerWareHouse_new'),
    # url('centerWareHouse_add', views.CenterWareHouseAddView.as_view(), name='centerWareHouse_add'),
    # url('centerWareHouse_update', views.CenterWareHouseUpdateView.as_view(), name='centerWareHouse_update'),

    # supplier
    url('suppliers', views.SuppliersView.as_view(), name='suppliers'),
    url('supplier_add', views.SupplierAddView.as_view(), name='supplier_add'),
    url('supplier_update', views.SupplierUpdateView.as_view(), name='supplier_update'),
    url('supplier_status', views.SupplierStatusView.as_view(), name='supplier_status'),

    # measure
    url('measures', views.MeasuresView.as_view(), name='measures'),
    url('measure_add', views.MeasureAddView.as_view(), name='measure_add'),
    url('measure_update', views.MeasureUpdateView.as_view(), name='measure_update'),
    url('measure_status', views.MeasureStatusView.as_view(), name='measure_status'),

    # material type
    url('material_types', views.MaterialTypesView.as_view(), name='material_types'),
    url('material_type_add', views.MaterialTypeAddView.as_view(), name='material_type_add'),
    url('material_type_update', views.MaterialTypeUpdateView.as_view(), name='material_type_update'),
    url('material_type_status', views.MaterialTypeStatusView.as_view(), name='material_type_status'),

    # material
    url('materials', views.MaterialsView.as_view(), name='materials'),
    url('material_new', views.MaterialNewView.as_view(), name='material_new'),
    url('material_add', views.MaterialAddView.as_view(), name='material_add'),
    url('material_update', views.MaterialUpdateView.as_view(), name='material_update'),
    url('material_status', views.MaterialStatusView.as_view(), name='material_status'),
]