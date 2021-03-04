# -*- coding: utf-8 -*-
# @Author:  ty
# @FileName: urls.py
# @Time:  2021/3/4 下午2:05
# @Description:
from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^login', views.LoginView.as_view(), name='login'),
    url(r'^loginExit', views.LoginExitView.as_view(), name='loginExit'),
    url(r'^user', views.UserView.as_view(), name='user'),
    url(r'^userNew', views.UserNewView.as_view(), name='userNew'),
    url(r'^userAdd', views.UserAddView.as_view(), name='userAdd'),
    url(r'^userUpdate', views.UserUpdateView.as_view(), name='userUpdate'),
    url(r'^userStatus', views.UserStatusView.as_view(), name='userStatus'),
    url(r'^users', views.UsersView.as_view(), name='users'),

    url(r'^areas', views.AreasView.as_view(), name='areas'),

    url(r'^roles', views.RolesView.as_view(), name='roles'),
    url(r'^roleAdd', views.RoleAddView.as_view(), name='roleAdd'),
    url(r'^roleUpdate', views.RoleUpdateView.as_view(), name='roleUpdate'),
    url(r'^roleStatus', views.RoleStatusView.as_view(), name='roleStatus'),

    url(r'^departments', views.DepartmentsView.as_view(), name='departments'),
    url(r'^departmentAdd', views.DepartmentAddView.as_view(), name='departmentAdd'),
    url(r'^departmentUpdate', views.DepartmentUpdateView.as_view(), name='departmentUpdate'),
    url(r'^departmentStatus', views.DepartmentStatusView.as_view(), name='departmentStatus'),
    url(r'^rolePermissionAddSave', views.RolePermissionAddSaveView.as_view(), name='rolePermissionAddSave'),

    url(r'^customers', views.CustomersView.as_view(), name='customers'),
    url(r'^customerAdd', views.CustomerAddView.as_view(), name='customerAdd'),
    url(r'^customerUpdate', views.CustomerUpdateView.as_view(), name='customerUpdate'),
    url(r'^customerStatus', views.CustomerStatusView.as_view(), name='customerStatus'),

    url(r'^organizations', views.OrganizationsView.as_view(), name='organizations'),
    url(r'^organizationNew', views.OrganizationNewView.as_view(), name='organizationNew'),
    url(r'^organizationAdd', views.OrganizationAddView.as_view(), name='organizationAdd'),
    url(r'^organizationUpdate', views.OrganizationUpdateView.as_view(), name='organizationUpdate'),
    url(r'^organizationStatus', views.OrganizationStatusView.as_view(), name='organizationStatus'),

    url(r'^brands', views.BrandsView.as_view(), name='brands'),
    url(r'^brandAdd', views.BrandAddView.as_view(), name='brandAdd'),
    url(r'^brandUpdate', views.BrandUpdateView.as_view(), name='brandUpdate'),
    url(r'^brandStatus', views.BrandStatusView.as_view(), name='brandStatus'),

    url(r'^totalWareHouses', views.TotalWareHousesView.as_view(), name='totalWareHouses'),
    url(r'^totalWareHouseNew', views.TotalWareHouseNewView.as_view(), name='totalWareHouseNew'),
    url(r'^totalWareHouseAdd', views.TotalWareHouseAddView.as_view(), name='totalWareHouseAdd'),
    url(r'^totalWareHouseUpdate', views.TotalWareHouseUpdateView.as_view(), name='totalWareHouseUpdate'),
    url(r'^totalWareHouseStatus', views.TotalWareHouseStatusView.as_view(), name='totalWareHouseUpdate'),

    url(r'^centers', views.CentersView.as_view(), name='centers'),
    url(r'^centerNew', views.CenterNewView.as_view(), name='centerNew'),
    url(r'^centerAdd', views.CenterAddView.as_view(), name='centerAdd'),
    url(r'^centerUpdate', views.CenterUpdateView.as_view(), name='centerUpdate'),
    url(r'^centerStatus', views.CenterStatusView.as_view(), name='centerStatus'),

    # url(r'^centerWareHouses', views.CenterWareHousesView.as_view(), name='centerWareHouses'),
    # url(r'^centerWareHouseNew', views.CenterWareHouseNewView.as_view(), name='centerWareHouseNew'),
    # url(r'^centerWareHouseAdd', views.CenterWareHouseAddView.as_view(), name='centerWareHouseAdd'),
    # url(r'^centerWareHouseUpdate', views.CenterWareHouseUpdateView.as_view(), name='centerWareHouseUpdate'),

    url(r'^suppliers', views.SuppliersView.as_view(), name='suppliers'),
    url(r'^supplierAdd', views.SupplierAddView.as_view(), name='supplierAdd'),
    url(r'^supplierUpdate', views.SupplierUpdateView.as_view(), name='supplierUpdate'),
    url(r'^supplierStatus', views.SupplierStatusView.as_view(), name='supplierStatus'),

    url(r'^measures', views.MeasuresView.as_view(), name='measures'),
    url(r'^measureAdd', views.MeasureAddView.as_view(), name='measureAdd'),
    url(r'^measureUpdate', views.MeasureUpdateView.as_view(), name='measureUpdate'),
    url(r'^measureStatus', views.MeasureStatusView.as_view(), name='measureStatus'),

    url(r'^materialTypes', views.MaterialTypesView.as_view(), name='materialTypes'),
    url(r'^materialTypeAdd', views.MaterialTypeAddView.as_view(), name='materialTypeAdd'),
    url(r'^materialTypeUpdate', views.MaterialTypeUpdateView.as_view(), name='materialTypeUpdate'),
    url(r'^materialTypeStatus', views.MaterialTypeStatusView.as_view(), name='materialTypeStatus'),

    url(r'^materials', views.MaterialsView.as_view(), name='materials'),
    url(r'^materialNew', views.MaterialNewView.as_view(), name='materialNew'),
    url(r'^materialAdd', views.MaterialAddView.as_view(), name='materialAdd'),
    url(r'^materialUpdate', views.MaterialUpdateView.as_view(), name='materialUpdate'),
    url(r'^materialStatus', views.MaterialStatusView.as_view(), name='materialStatus'),

    # url(r'^area',)
]