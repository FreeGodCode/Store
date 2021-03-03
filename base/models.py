from django.db import models


class UserNow(models.Model):
    """当前登录用户的信息用于全局使用，只存一条信息，同时可以修改"""
    user_id = models.IntegerField(verbose_name='人员id')
    user_identify = models.CharField(max_length=20, verbose_name='登录工号')
    user_name = models.CharField(max_length=20, verbose_name='登录人名字')
    area_name = models.CharField(max_length=20, verbose_name='登录人区域')
    user_departments = models.CharField(max_length=20, verbose_name='登录人部门')
    user_roles = models.CharField(max_length=20, verbose_name='登录人角色')

    def __str__(self):
        return self.user_name

    class Meta:
        db_table = 'db_user'
        verbose_name = "当前登录"


class UserProfile(AbstractUser):
    """定义员工信息"""
    USER_STATUS_CHOICES = (
        (0, '停用'),
        (1, '启用'),
    )
    id = models.AutoField(primary_key=True)
    # user_id = models.CharField(max_length=20, verbose_name='工号')
    # user_passwd = models.CharField(max_length=80, default=user_id, verbose_name='用户密码')
    user_name = models.CharField(max_length=20, verbose_name='姓名')
    user_phone_number = models.CharField(max_length=20, unique=True, verbose_name='手机号', null=True)
    user_mailbox = models.CharField(max_length=30, unique=True, verbose_name='邮箱', null=True)
    area_name = models.CharField(max_length=20, verbose_name='区域')
    area = models.ForeignKey('Area', verbose_name='区域', related_name='area_user', on_delete=models.CASCADE)
    user_status = models.IntegerField(choices=USER_STATUS_CHOICES, default=0, verbose_name='用户状态')
    user_departments = models.CharField(max_length=50, null=True, verbose_name='部门')
    user_roles = models.CharField(max_length=50, null=True, verbose_name='角色')
    user_creator = models.CharField(max_length=20, verbose_name='员工创建人名字')
    user_creator_identify = models.CharField(max_length=20, verbose_name='员工创建人工号')

    # user_creator = models.ForeignKey('UserProfile',verbose_name='用户',on_delete=models.CASCADE)

    user_created_at = models.DateTimeField(auto_now_add=True, verbose_name='员工创建时间')

    class Meta:
        db_table = 'db_user_profile'
        verbose_name = "员工"

    def __str__(self):
        return self.user_name


class Department(models.Model):
    """部门"""
    DP_CHOICES = (
        (0, '非中心部门'),
        (1, '中心'),
    )
    DP_STATUS_CHOICES = (
        (0, '停用'),
        (1, '启用'),
    )
    id = models.AutoField(primary_key=True)
    dpm_name = models.CharField(max_length=20, verbose_name='部门名称')
    dpm_status = models.IntegerField(choices=DP_STATUS_CHOICES, default=0, verbose_name='部门状态')
    dpm_remarks = models.TextField(max_length=400, verbose_name='部门备注', null=True)
    dpm_center = models.IntegerField(choices=DP_CHOICES, default=0, verbose_name='是否中心')
    dpm_creator = models.CharField(max_length=20, verbose_name='部门创建人名字')
    dpm_creator_identify = models.CharField(max_length=20, verbose_name='部门创建人工号')
    dpm_createDate = models.DateTimeField(auto_now_add=True, verbose_name='部门创建时间')

    def __str__(self):
        return self.dpm_name

    class Meta:
        db_table = 'db_department'
        verbose_name = "部门"


class Role(models.Model):
    """角色"""
    ROLE_STATUS_CHOICES = (
        (0, '停用'),
        (1, '启用')
    )
    id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=15, unique=True, verbose_name='角色名称')
    role_status = models.IntegerField(choices=ROLE_STATUS_CHOICES, default=0, verbose_name='角色状态')
    role_permission = models.CharField(max_length=60, verbose_name='角色权限', null=True)
    role_description = models.TextField(max_length=400, verbose_name='角色描述', null=True)
    role_creator = models.CharField(max_length=20, verbose_name='角色创建人名字')
    role_creator_identify = models.CharField(max_length=20, verbose_name='角色创建人工号')
    role_created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建角色时间")

    def __str__(self):
        return self.role

    class Meta:
        db_table = 'db_role'
        verbose_name = "角色"


class Organization(models.Model):
    """定义组织"""
    ORG_STATUS_CHOICES = (
        (0, '停用'),
        (1, '启用')
    )
    id = models.AutoField(primary_key=True)
    org_identify = models.CharField(max_length=6, unique=True, verbose_name='组织编码')
    org_name = models.CharField(max_length=20, verbose_name='组织名称')
    area_name = models.CharField(max_length=20, verbose_name='区域')
    org_status = models.IntegerField(choices=ORG_STATUS_CHOICES, default=0, verbose_name='组织状态')
    # area = models.ForeignKey('Area', verbose_name='区域', related_name='area_orga', on_delete=models.CASCADE)
    org_remarks = models.TextField(max_length=400, verbose_name='组织备注', null=True)
    org_creator = models.CharField(max_length=20, verbose_name='组织创建者名字')
    org_creator_identify = models.CharField(max_length=20, verbose_name='组织创建者工号')
    org_created_at = models.DateTimeField(auto_now_add=True, verbose_name="组织创建时间")
    org_modified_at = models.DateTimeField(auto_now_add=True, verbose_name="组织修改时间")

    class Meta:
        db_table = 'db_organization'
        verbose_name = "组织"

    def __str__(self):
        return self.org_name


class Area(models.Model):
    """区域"""
    AREA_STATUS_CHOICES = (
        (0, '停用'),
        (1, '启用'),
    )
    id = models.AutoField(primary_key=True)
    area_name = models.CharField(max_length=8, verbose_name='区域名称')
    area_status = models.IntegerField(choices=AREA_STATUS_CHOICES, default=0, verbose_name='区域状态')

    class Meta:
        db_table = 'db_area'
        verbose_name = "区域"

    def __str__(self):
        return self.area_name


# class Permission(models.Model):
#     """权限""
#
#     id = models.AutoField(primary_key=True)
#     permission_name = models.CharField(max_length=20, verbose_name='权限名字')

#     def __str__(self):
#         return self.permission_name

# class Meta:
#     db_table = 'db_permission'
#     verbose_name = '权限'


class Brand(models.Model):
    """品牌"""
    BRAND_STATUS_CHOICES = (
        (0, '停用'),
        (1, '启用')
    )
    id = models.AutoField(primary_key=True)
    brand_name = models.CharField(max_length=20, verbose_name='品牌名称')
    brand_status = models.IntegerField(choices=BRAND_STATUS_CHOICES, default=1, verbose_name='品牌状态')
    brand_description = models.TextField(max_length=400, verbose_name='品牌描述', null=True)
    brand_creator = models.CharField(max_length=20, verbose_name='品牌创建者名字')
    brand_creator_identify = models.CharField(max_length=20, verbose_name='品牌创建者工号')
    brand_created_at = models.DateTimeField(auto_now_add=True, verbose_name='品牌创建时间')
    brand_modified_at = models.DateTimeField(auto_now_add=True, verbose_name='品牌修改时间')

    class Meta:
        verbose_name = "品牌"

    def __str__(self):
        return self.brand_name


class TotalWareHouse(models.Model):
    """总仓库"""
    TOTAL_STATUS_CHOICES = (
        (0, '停用'),
        (1, '启用')
    )
    id = models.AutoField(primary_key=True)
    total_identify = models.CharField(max_length=6, unique=True, verbose_name='总仓库编码')
    total_name = models.CharField(max_length=20, verbose_name='总仓名字')
    organization = models.ForeignKey('Organization', related_name='org_total_ware_house', on_delete=models.CASCADE)
    total_status = models.IntegerField(choices=TOTAL_STATUS_CHOICES, default=1, verbose_name='总仓状态')
    total_belong_center = models.CharField(max_length=20, verbose_name='所属中心的名字', null=True)
    total_belong_center_identify = models.CharField(max_length=20, verbose_name='所属中心的编号', null=True)
    brand = models.ForeignKey('Brand', verbose_name='品牌', on_delete=models.CASCADE)
    brand_name = models.CharField(max_length=20, verbose_name='品牌名称', null=True)
    total_remarks = models.TextField(max_length=400, verbose_name='总仓备注')
    total_creator = models.CharField(max_length=20, verbose_name="总仓创建者名字")
    total_creator_identify = models.CharField(max_length=20, verbose_name="总仓创建者工号")
    total_created_at = models.DateTimeField(auto_now_add=True, verbose_name='总仓创建时间')
    total_modified_at = models.DateTimeField(auto_now_add=True, verbose_name='总仓创建时间')

    class Meta:
        db_table = 'db_warehouse'
        verbose_name = "总仓"

    def __str__(self):
        return self.total_name


class CenterWareHouse(models.Model):
    """中心仓库"""
    CENTER_WH_STATUS_CHOICES = (
        (0, '停用'),
        (1, '启用')
    )
    id = models.AutoField(primary_key=True)
    center_wh_identify = models.CharField(max_length=6, unique=True, verbose_name='中心仓库编码')
    center_wh_name = models.CharField(max_length=20, verbose_name='中心仓库名字')
    organization = models.ForeignKey('Organization', related_name='org_center_ware_house', verbose_name='组织', on_delete=models.CASCADE)
    center = models.ForeignKey('Center', related_name='center_center_wh', verbose_name='所属中心', on_delete=models.CASCADE)
    center_wh_status = models.IntegerField(choices=CENTER_WH_STATUS_CHOICES, default=1, verbose_name='中心仓库状态')
    brand = models.ForeignKey('Brand', verbose_name='品牌', on_delete=models.CASCADE)
    brand_name = models.CharField(max_length=20, verbose_name='品牌名称')
    center_wh_remarks = models.TextField(max_length=400, verbose_name='中心仓库备注', null=True)
    center_wh_creator = models.CharField(max_length=20, verbose_name="中心创建者")
    center_wh_created = models.DateTimeField(auto_now_add=True, verbose_name='中心创建时间')

    class Meta:
        db_table = 'db_center_wh'
        verbose_name = "中心仓库"

    def __str__(self):
        return self.center_wh_name


class Supplier(models.Model):
    """供应商"""
    SUPPLY_STATUS_CHOICES = (
        (0, '停用'),
        (1, '启用')
    )
    SUPPLY_TYPE_CHOICES = (
        (0, '内部单位'),
        (1, '外部单位')
    )
    id = models.AutoField(primary_key=True)
    supply_identify = models.CharField(max_length=7, unique=True, verbose_name='供应商编码')
    supply_name = models.CharField(max_length=20, verbose_name='供应商名称')
    supply_type = models.IntegerField(choices=SUPPLY_TYPE_CHOICES, default=0, verbose_name="供应商类型")
    supply_remarks = models.TextField(max_length=400, verbose_name='供应商备注', null=True)
    supply_status = models.IntegerField(choices=SUPPLY_STATUS_CHOICES, default=0, verbose_name='供应商状态')
    supply_creator = models.CharField(max_length=20, verbose_name='供应商创建者名字')
    supply_creator_identify = models.CharField(max_length=20, verbose_name='供应商创建者工号')
    supply_created_at = models.DateTimeField(auto_now_add=True, verbose_name='供应商创建时间')
    supply_modified_at = models.DateTimeField(auto_now_add=True, verbose_name='供应商修改时间')

    class Meta:
        db_table = 'db_supplier'
        verbose_name = "供应商"

    def __str__(self):
        return self.supply_name


class Center(models.Model):
    """中心"""
    CENTER_STATUS_CHOICES = (
        (0, '停用'),
        (1, '启用')
    )
    id = models.AutoField(primary_key=True)
    # center_identify = models.CharField(max_length=8,verbose_name='中心编号')
    center_name = models.CharField(max_length=20, verbose_name='中心名称')
    area_name = models.CharField(max_length=20, verbose_name='区域')
    area = models.ForeignKey('Area', verbose_name='区域', related_name='area_center', on_delete=models.CASCADE)
    center_remarks = models.TextField(max_length=400, verbose_name='中心备注', null=True)
    center_status = models.IntegerField(choices=CENTER_STATUS_CHOICES, default=0, verbose_name='中心状态')
    center_creator = models.CharField(max_length=20, verbose_name='中心创建者名字')
    center_creator_identify = models.CharField(max_length=20, verbose_name='中心创建者工号')
    center_created_at = models.DateTimeField(auto_now_add=True, verbose_name='中心创建时间')
    center_modified_at = models.DateTimeField(auto_now_add=True, verbose_name='中心修改时间')

    class Meta:
        db_table = 'db_center'
        verbose_name = "中心"

    def __str__(self):
        return self.center_name


class Customer(models.Model):
    """
    客户
    """
    CUSTOMER_TYPE_CHOICES = (
        (0, '内部单位'),
        (1, '外部单位')
    )
    CUSTOMER_STATUS_CHOICES = (
        (0, '停用'),
        (1, '启用')
    )
    id = models.AutoField(primary_key=True)
    customer_identify = models.CharField(max_length=7, unique=True, verbose_name='客户编码')
    customer_name = models.CharField(max_length=20, verbose_name='客户名称')
    customer_type = models.IntegerField(choices=CUSTOMER_TYPE_CHOICES, default=0, verbose_name="客户类型")
    customer_remarks = models.TextField(max_length=400, verbose_name='客户备注', null=True)
    customer_status = models.IntegerField(choices=CUSTOMER_STATUS_CHOICES, default=0, verbose_name='客户状态')
    customer_creator = models.CharField(max_length=20, verbose_name='客户创建者名字')
    customer_creator_identify = models.CharField(max_length=20, verbose_name='客户创建者工号')
    customer_created_at = models.DateTimeField(auto_now_add=True, verbose_name='客户创建时间')
    customer_modified_at = models.DateTimeField(auto_now_add=True, verbose_name='客户修改时间')

    class Meta:
        db_table = "db_customer"
        verbose_name = "客户"

    def __str__(self):
        return self.customer_name


class Measure(models.Model):
    """计量单位"""
    MEASURE_DIMENSION_CHOICES = (
        (0, '重量'),
        (1, '长度'),
        (2, '面积'),
        (3, '体积'),
        (4, '件数')
    )
    MEASURE_STATUS_CHOICES = (
        (0, '停用'),
        (1, '启用')
    )
    id = models.AutoField(primary_key=True)
    measure_identify = models.CharField(max_length=6, unique=True, verbose_name='计量单位编码')
    measure_name = models.CharField(max_length=20, verbose_name='计量单位名称')
    measure_dimension = models.IntegerField(choices=MEASURE_DIMENSION_CHOICES, verbose_name="计量单位量纲")
    measure_status = models.IntegerField(choices=MEASURE_STATUS_CHOICES, default=0, verbose_name='计量单位状态')
    measure_creator = models.CharField(max_length=20, verbose_name='计量单位创建者名字')
    measure_creator_identify = models.CharField(max_length=20, verbose_name='计量单位创建者工号')
    measure_created_at = models.DateTimeField(auto_now_add=True, verbose_name='计量单位创建时间')
    measure_modified_at = models.DateTimeField(auto_now_add=True, verbose_name='计量单位修改时间')

    class Meta:
        db_table = 'db_measure'
        verbose_name = "计量单位"

    def __str__(self):
        return self.meterage_name


class MaterialType(models.Model):
    """物料类别"""
    TYPE_STATUS_CHOICES = (
        (0, '停用'),
        (1, '启用')
    )
    id = models.AutoField(primary_key=True)
    type_identify = models.CharField(max_length=30, unique=True, verbose_name='物料类别编码')
    type_name = models.CharField(max_length=20, verbose_name='物料类别名称')
    type_status = models.IntegerField(choices=TYPE_STATUS_CHOICES, default=0, verbose_name='物料类别状态')
    type_creator = models.CharField(max_length=20, verbose_name='物料类别创建者名字')
    type_creator_identify = models.CharField(max_length=20, verbose_name='物料类别创建者工号')
    type_created_at = models.DateTimeField(auto_now_add=True, verbose_name='物料创建时间')
    type_modified_at = models.DateTimeField(auto_now_add=True, verbose_name='物料修改时间')

    class Meta:
        db_table = 'db_material_type'
        verbose_name = "物料类别"

    def __str__(self):
        return self.type_name


class Material(models.Model):
    """物料"""
    MATERIAL_DIMENSION_CHOICES = (
        (0, '存货'),
        (1, '固定资产'),
        (2, '费用')
    )
    MATERIAL_STATUS_CHOICES = (
        (0, '停用'),
        (1, '启用')
    )
    # 物料编码除了后五位其它全为分类编码
    id = models.AutoField(primary_key=True)
    material_identify = models.CharField(max_length=35, unique=True, verbose_name='物料编码')
    material_name = models.CharField(max_length=20, verbose_name='物料名称')
    material_specification = models.CharField(max_length=30, verbose_name='物料规格')
    material_model = models.CharField(max_length=30, verbose_name='物料型号')
    measure_name = models.CharField(max_length=20, verbose_name='计量单位名称')
    material_type_identify = models.CharField(max_length=30, verbose_name='分类编码')
    # meterage = models.ForeignKey('Meterage', verbose_name='计量单位', related_name='meterage_material',
    #                              on_delete=models.CASCADE)
    material_attr = models.IntegerField(choices=MATERIAL_DIMENSION_CHOICES, verbose_name='存货属性')
    material_status = models.IntegerField(choices=MATERIAL_STATUS_CHOICES, default=0, verbose_name='物料状态')
    material_creator = models.CharField(max_length=20, verbose_name='物料创建者名字')
    material_creator_identify = models.CharField(max_length=20, verbose_name='物料创建者工号')
    material_created_at = models.DateTimeField(auto_now_add=True, verbose_name='物料创建时间')
    material_modified_at = models.DateTimeField(auto_now_add=True, verbose_name='物料修改时间')

    class Meta:
        db_table = 'db_material'
        verbose_name = "物料"

    def __str__(self):
        return self.material_name
