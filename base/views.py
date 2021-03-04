import logging
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Max, Q
from rest_framework.views import APIView
from .models import UserProfile, UserNow, Measure,  Material, MaterialType, Center, Customer, CenterWareHouse,TotalWareHouse, Supplier, Department, Brand, Role, Organization, Area
from .serializer import CustomerSerializer, CenterSerializer, CenterWareHouseSerializer, DepartmentSerializer, BrandSerializer, AreaSerializer, TotalWareHouseSerializer, MaterialSerializer, MeasureSerializer,MaterialTypeSerializer,SupplierSerializer, RoleSerializer, OrganizationSerializer,UserProfileSerializer

logger = logging.getLogger(__name__)


def department_to_list(dpm_name_list):
    """"""
    dep_list = []
    for dpm_name in dpm_name_list:
        id = str(Department.objects.get(dpm_name=dpm_name).id)
        dep_list.append(id)
    dep_name = '-'.join(dep_list)
    return dep_name


def role_to_list(roles_name_list):
    role_list = []
    for role_name in roles_name_list:
        id = str(Role.objects.get(role=role_name).id)
        role_list.append(id)
    role_name = '-'.join(role_list)
    return role_name


class LoginView(APIView):
    """登录"""

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        user_identify = data['user_identify']
        user_passwd = data['user_passwd']
        user_now = UserNow.objects.filter(user_identify=user_identify)
        logger.info('now user is user_now')
        if user_now:
            return HttpResponse({'message': '用户已登录'})
        else:
            try:
                user = authenticate(username=user_identify, password=user_passwd)
            except UserProfile.DoesNotExist:
                return HttpResponse({'message': '登录异常', 'signal': '3'})
            else:
                if user:
                    if user.is_active == 1:
                        login(request, user)
                        user = UserProfile.objects.get(username=user_identify)
                        user_id = user.id
                        username = user.username
                        user_name = user.user_name
                        area_name = user.area_name
                        user_departments = user.user_departments
                        user_roles = user.user_roles
                        UserNow.objects.create(user_id=user_id, user_identify=user_identify, user_name=user_name,
                                               area_name=area_name, user_departments=user_departments,
                                               user_roles=user_roles)
                        user_roles = user.user_roles
                        roles = []
                        if user_roles:
                            user_roles_list = list(map(int, user_roles.split('-')))
                            for user_role in user_roles_list:
                                role_message = []
                                try:
                                    role = Role.objects.get(id=user_role, role_status=1)
                                except Role.DoesNotExist:
                                    pass
                                else:
                                    role_message.append(role.role)
                                    role_message.append(role.role_power)
                                    roles.append(role_message)
                        user_serializer = UserProfileSerializer(user)
                        return HttpResponse(
                            {'message': '登录成功', 'signal': '0', 'roles': roles, 'user': user_serializer.data})
                    elif user.is_active == 0:
                        return HttpResponse({'message': '账号为激活', 'signal': '1'})
                else:
                    return HttpResponse({'message': '用户名或密码错误', 'signal': '2'})


class LoginExitView(APIView):
    """退出"""

    def post(self, request):
        data = json.loads(request.body.decode('utf_8'))
        user_identify = data['user_identify']
        try:
            user_now = UserNow.objects.get(user_identify=user_identify)
        except UserNow.DoesNotExist:
            return HttpResponse({'message': '未登录', 'signal': 1})
        else:
            logout(request)
            user_now.delete()
            return HttpResponse({'message': '退出登录成功', 'signal': 0})


class UserView(APIView):
    """用户信息"""

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        user_identify = data['user_identify']
        user = UserNow.objects.filter(user_identify=user_identify)
        if user:
            try:
                user_profile = UserProfile.objects.get(username=user.user_identify)
            except UserProfile.DoesNotExist:
                return HttpResponse({'message': '用户信息不存在'})
            else:
                user_serializer = UserProfileSerializer(user_profile)
                return HttpResponse({'user': user_serializer.data})
        return HttpResponse({'message': '用户未登录'})


class UserNewView(APIView):
    """"""

    def get(self, request):
        max_id = UserProfile.objects.all().aggregate(Max('username'))['username__max']
        departments = Department.objects.filter(dpm_status=1).values_list('dpm_name', fiat=True)
        roles = Role.objects.filter(role_status=1).values_list('role', flat=True)
        areas = Area.objects.filter(area_status=1).values_list('area_name', flat=True)
        return HttpResponse({'max_identify': max_id, 'departments': departments, 'roles': roles, 'areas': areas})


class UserAddView(APIView):
    """新增"""

    def __init__(self, **kwargs):
        super(UserAddView, self).__init__(**kwargs)
        self.message = '注册成功'
        self.signal = 0
        self.user_now_name = ''

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        user_identify = data['user_identify']
        user = UserNow.objects.get(user_identify=user_identify)
        if user:
            self.user_now_name = user.user_name
        username = data['username']
        password = data['password']
        user_name = data['user_name']
        user_phone_number = data['user_phone_number']
        email = data['email']
        user_departments = department_to_list(data['user_departments'])
        user_roles = role_to_list(data['user_roles'])
        area_name = data['area_name']
        # 检查员工id, phone, email是否存在，不存在时才能创建新的员工
        if self.idCheck(username):
            if self.phoneCheck(user_phone_number):
                if self.emailCheck(email):
                    UserProfile.objects.create_user(username=username, password=password, user_name=user_name,
                                                    user_phone_number=user_phone_number, email=email, is_active=0,
                                                    user_departments=user_departments, user_roles=user_roles,
                                                    user_creator=self.user_now_name,
                                                    user_creator_identify=user_identify, area_name=area_name)
                    # pass
        return HttpResponse({'message': self.message, 'signal': self.signal})

    def idCheck(self, user_identify):
        """员工id校验"""
        try:
            user = UserProfile.objects.get(username=user_identify)
        except UserProfile.DoesNotExist:
            return True
        else:
            self.message = '员工id已存在'
            self.signal = 1
            return False

    def phoneCheck(self, phone):
        """员工电话校验"""
        try:
            user = UserProfile.objects.get(user_phone_number=phone)
        except UserProfile.DoesNotExist:
            return True
        else:
            self.message = '员工电话号码已经存在'
            self.signal = 2
            return False

    def emailCheck(self, email):
        """员工邮箱校验"""
        try:
            user = UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            return True
        else:
            self.message = '员工邮箱已存在'
            self.signal = 3
            return False


class UserUpdateView(APIView):
    """更新"""

    def __init__(self, **kwargs):
        super(UserUpdateView, self).__init__(**kwargs)
        self.message = '修改成功'
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        id = data['id']
        username = data['username']
        user_name = data['user_name']
        user_phone_number = data['user_phone_number']
        email = data['email']
        user_departments = department_to_list(data['user_departments'])
        user_roles = role_to_list(data['user_roles'])
        area_name = data['area_name']
        user = UserProfile.objects.filter(id=id)
        if self.idCheck(username, id):
            if self.phoneCheck(user_phone_number, id):
                if self.emailCheck(email, id):
                    if user:
                        user.update(username=username, user_name=user_name, user_phone_number=user_phone_number,
                                    email=email, user_departments=user_departments, user_roles=user_roles,
                                    area_name=area_name)
                    else:
                        self.message = '员工查询出错'
                        self.signal = 1

        return HttpResponse({'message': self.message, 'signal': self.signal})

    def idCheck(self, user_identify, id):
        try:
            user = UserProfile.objects.get(~Q(id=id), username=user_identify)
        except UserProfile.DoesNotExist:
            return True
        else:
            self.message = '员工id已存在'
            self.signal = 1
            return False

    def phoneCheck(self, phone, id):
        try:
            user = UserProfile.objects.get(~Q(id=id), user_phone_number=phone)
        except UserProfile.DoesNotExist:
            return True
        else:
            self.message = '员工电话号码已存在'
            self.signal = 2
            return False

    def emailCheck(self, email, id):
        try:
            user = UserProfile.objects.get(~Q(id=id), email=email)
        except UserProfile.DoesNotExist:
            return True
        else:
            self.message = '员工邮箱已存在'
            self.signal = 3
            return False


class UserStatusView(APIView):
    """用户状态"""

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        is_active = data['is_active']
        username = data['username']
        user = UserProfile.objects.filter(username=username)
        if user:
            user.update(is_active=is_active)
            return Response({'message': '状态更改成功', 'signal': 0})
        else:
            return Response({'message': '未查询到用户，状态更该失败'})


class UsersView(APIView):
    """"""

    def get(self, request):
        users = UserProfile.objects.all()
        if users:
            departments_list = []
            roles_list = []
            users_serializer = UserProfileSerializer(users, many=True)
            for user in users:
                department_list = []
                role_list = []
                departments = user.user_departments
                if departments:
                    departments = departments.split('-')
                else:
                    departments = []

                roles = user.user_roles
                if roles:
                    roles = roles.split('-')
                else:
                    roles = []

                if user.user_departments:
                    for department in departments:
                        department_list.append(Department.objects.get(id=department).dpm_name)

                if user.user_roles:
                    for role in roles:
                        role_list.append(Role.objects.get(id=role).role)

                departments_list.append(department_list)
                roles_list.append(role_list)
            return HttpResponse({'users': users_serializer.data, 'departments': departments_list, 'roles': roles_list})


class AreasView(APIView):
    """区域管理"""

    def get(self, request):
        areas = Area.objects.filter(area_staatus=1).all()
        if areas:
            areas_serializer = AreaSerializer(areas, many=True)
            return Response({'areas': areas_serializer.data})
        else:
            return Response({'message': '查询结果为空'})


class RolesView(APIView):
    """角色维护"""

    def get(self, request):
        roles = Role.objects.all()
        if roles:
            roles_serializer = RoleSerializer(roles, many=True)
            return Response({'roles': roles_serializer.data})
        else:
            return Response({'message': '未查询到角色信息'})


class RoleAddView(APIView):
    """添加"""

    def __init__(self, **kwargs):
        super(RoleAddView, self).__init__(**kwargs)
        self.message = '添加成功'
        self.signal = 0
        self.user_now_name = ''

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        user_identify = data['user_identify']
        user_now = UserNow.objects.get(user_identify=user_identify)
        role = data['role']
        role_permission = data['role_permission']
        role_description = data['role_description']
        if user_now:
            self.user_now_name = user_now.user_name
            if self.nameCheck(role):
                Role.objects.create(role=role, role_permission=role_permission, role_description=role_description,
                                    role_status=0, role_creator=self.user_now_name, role_creator_identify=user_identify)
        else:
            self.message = '用户未登录'
            self.signal = 2

        return Response({'message': self.message, 'signal': self.signal})

    def roleCheck(self, role_name):
        try:
            role = Role.objects.get(role=role_name)
        except Role.DoesNotExist:
            return True
        else:
            self.message = '角色已经存在'
            self.signal = 1
            return False


class RoleUpdateView(APIView):
    """更新"""

    def __init__(self, **kwargs):
        super(RoleUpdateView, self).__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        id = data['id']
        role = data['role']
        role_permission = data['role_permission']
        role_description = data['role_description']
        if self.roleCheck(role, id):
            try:
                Role.objects.filter(id=id).update(role_permission=role_permission, role=role,
                                                  role_description=role_description)
            except:
                self.message = '更新失败'
                self.signal = 1

        return Response({'message': self.message, 'signal': self.signal})

    def roleCheck(self, role_name, id):
        try:
            role = Role.objects.get(~Q(id=id), role=role_name)
        except Role.DoesNotExist:
            return True
        else:
            self.message = '角色名已存在'
            self.signal = 2
            return False


class RoleStatusView(APIView):
    """角色状态更新"""

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        id = data['id']
        role_status = data['role_status']
        role = Role.objects.filter(id=id)
        if role:
            role.update(role_status=role_status)
            return Response({'message': '状态更新成功', 'signal': 200})
        else:
            return Response({'message': '未查询到角色， 状态更新失败'})


class RolePermissionAddSaveView(APIView):
    """角色权限添加"""

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        id = data['id']
        role_permission = data['role_permission']
        try:
            Role.objects.get(id=id).Update(role_permission=role_permission)
        except:
            return Response({'message': '权限更新失败', 'signal': 0})
        else:
            return Response({'message': '权限添加成功', 'signal': 0})


class CustomersView(APIView):
    """获取所有客户"""

    def get(self, request):
        max_id = Customer.objects.all().aggregate(Max('customer_identify'))['customer_identify__max']
        customers = Customer.objects.all()
        if customers:
            customers_serializer = CustomerSerializer(customers, many=True)
            return Response({'max_id': max_id, 'customers': customers_serializer.data})
        else:
            return Response({'message': '未查询到消息'})


class CustomerAddView(APIView):
    """添加客户"""

    def __init__(self, **kwargs):
        super(CustomerAddView, self).__init__(**kwargs)
        self.message = "添加成功"
        self.signal = 0
        self.user_now_name = ""

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        user_identify = data['user_identify']
        user_now = UserNOw.objects.get(user_identify=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name

        customer_identify = data['customer_identify']
        customer_name = data['customer_name']
        customer_type = data['customer_type']
        customer_remarks = data['customer_remarks']

        if self.idCheck(customer_identify):
            if self.nameCheck(customer_name):
                Customer.objects.create(customer_identify=customer_identify, customer_name=customer_name,
                                        customer_type=customer_type, customer_remarks=customer_remarks,
                                        customer_status=0, customer_creator=self.user_now_name,
                                        customer_creator_identiry=user_identify)

    def idCheck(self, customer_idenify):
        try:
            user = Customer.objects.get(customer_idenify=customer_idenify)
        except Customer.DoesNotExist:
            return True
        else:
            self.message = "客户id已存在"
            self.signal = 1
            return False

    def nameCheck(self, customer_name):
        try:
            user = Customer.objects.get(customer_name=customer_name)
        except Customer.DoesNotExist:
            return True
        else:
            self.message = "客户名已经存在"
            self.signal = 1
            return False


class CustomerUpdateView(APIView):
    """更新客户"""

    def __init__(self, **kwargs):
        super(CustomerUpdateView, self).__init__(**kwargs)
        self.message = '更新成功'
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        id = data['id']
        customer_identify = data['customer_identify']
        customer_name = data['customer_name']
        customer_type = data['customer_type']
        customer_remarks = data['customer_remarks']
        customer_status = data['customer_status']
        customer_creator = data['customer_creator']
        if self.idCheck(customer_identify, id):
            if self.nameCheck(customer_name, id):
                try:
                    Customer.objects.filter(id=id).update(customer_name=customer_name,
                                                          customer_identify=customer_identify,
                                                          customer_type=customer_type,
                                                          customer_remarks=customer_remarks,
                                                          customer_status=customer_status,
                                                          customer_creator=customer_creator)
                except:
                    self.message = '更新失败'
                    self.signal = 2

        return Response({'messaage': self.message, 'signal': self.signal})

    def idCheck(self, customer_identify, id):
        try:
            customer = Customer.objects.get(~Q(id=id), customer_identify=customer_identify)
        except Customer.DoesNotExist:
            return True
        else:
            self.message = '客户id已经存在'
            self.signal = 1
            return False

    def nameCheck(self, customer_name, id):
        try:
            customer = Customer.objects.get(~Q(id=id), customer_name=customer_name)
        except Customer.DoesNotExist:
            return True
        else:
            self.message = '客户已经存在'
            self.signal = 1
            return False


class CustomerStatusView(APIView):
    """更新客户状态"""

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        customer_status = data['customer_status']
        customer_identify = data['customer_identify']
        customer = Customer.objects.filter(customer_identify=customer_identify)
        if customer:
            customer.update(customer_status=customer_status)
            return Response({'message': '状态更新成功', 'signal': 0})
        else:
            return Response({'message': '未查询到客户， 状态更改失败'})


class OrganizationsView(APIView):
    """组织接口"""

    def get(self, request):
        max_id = Organization.objects.all().aggregate(Max('org_identify'))['org_identify__max']
        organizations = Organization.objects.all()
        if organizations:
            organizations_serializer = OrganizationSerializer(organizations, many=True)
            return Response({'max_identify': max_id, 'organizations': organizations_serializer.data})
        else:
            return Response({'message': '未查询到组织信息'})


class OrganizationNewView(APIView):
    """"""

    def get(self, request):
        areas = Area.objects.filter(area_status=1).values_list('area_name', flat=True)
        return Response({'areas': areas})


class OrganizationAddView(APIView):
    """新增组织"""

    def __init__(self, **kwargs):
        super(OrganizationAddView, self).__init__(**kwargs)
        self.message = '添加成功'
        self.signal = 0
        self.use_now_name = ''

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        user_identify = data['user_identify']
        user_now = UserNow.objects.get(user_identify=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
        org_identify = data['org_identify']
        org_name = data['org_name']
        area_name = data['area_name']
        org_remarks = data['org_remarks']
        if self.idCheck(org_identify):
            if self.nameCheck(org_name):
                Organization.objects.create(org_identify=org_identify, org_name=org_name, area_name=area_name,
                                            org_remarks=org_remarks, org_status=0, org_creator=self.user_now_name,
                                            org_creator_identify=user_identify)
        return Response({'message': self.message, 'signal': self.signal})

    def idCheck(self, org_identify):
        try:
            org = Organization.objects.get(org_identify=org_identify)
        except Organization.DoesNotExist:
            return True
        else:
            self.message = "组织id已存在"
            self.signal = 1
            return False

    def nameCheck(self, org_name):
        try:
            org_name = Organization.objects.get(org_name=org_name)
        except Organization.DoesNotExist:
            return True
        else:
            self.message = "组织名已经存在"
            self.signal = 1
            return False


class OrganizationUpdateView(APIView):
    """更新组织"""

    def __init__(self, **kwargs):
        super(OrganizationUpdateView, self).__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data["id"]
        org_identify = data['org_identify']
        org_name = data['org_name']
        org_remarks = data['org_remarks']
        # org_creator = data['org_creator']
        if self.idCheck(org_identify, id):
            if self.nameCheck(org_name, id):
                try:
                    Organization.objects.filter(id=id).update(org_identify=org_identify, org_name=org_name,
                                                              org_remarks=org_remarks, )
                except:
                    self.message = "更新失败"
                    self.signal = 2
        return Response({'message': self.message, 'signal': self.signal})

    def idCheck(self, org_identify, id):
        try:
            org = Organization.objects.get(~Q(id=id), org_identify=org_identify)
        except Organization.DoesNotExist:
            return True
        else:
            self.message = "组织id已存在"
            self.signal = 1
            return False

    def nameCheck(self, org_name, id):
        try:
            org = Organization.objects.get(~Q(id=id), org_name=org_name)
        except Organization.DoesNotExist:
            return True
        else:
            self.message = "组织名已经存在"
            self.signal = 1
            return False


class OrganizationStatusView(APIView):
    """"""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))

        org_status = data['org_status']
        org_identify = data['org_identify']

        organization = Organization.objects.filter(org_identify=org_identify)

        if organization:
            organization.update(org_status=org_status)
            return Response({"message": "状态更改成功", "signal": 0})
        else:
            return Response({"message": "未查询到组织,状态更改失败"})


class DepartmentsView(APIView):
    """部门视图接口"""

    def get(self, request):
        dpms = Department.objects.all()
        if dpms:
            dpms_serializer = DepartmentSerializer(dpms, many=True)
            return Response({"departments": dpms_serializer.data})
        else:
            return Response({"message": "未查询到部门信息"})


class DepartmentAddView(APIView):

    def __init__(self, **kwargs):
        super(DepartmentAddView, self).__init__(**kwargs)
        self.message = "添加成功"
        self.signal = 0
        self.user_now_name = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_identify']
        user_now = UserNow.objects.get(user_identify=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
        dpm_name = data['dpm_name']
        dpm_remarks = data['dpm_remarks']
        dpm_center = data['dpm_center']
        user_now = UserNow.objects.get(user_identify=user_identify)
        if user_now:
            if self.nameCheck(dpm_name):
                models.Department.objects.create(dpm_name=dpm_name, dpm_remarks=dpm_remarks, dpm_status=0,
                                                 dpm_center=dpm_center, dpm_creator=self.user_now_name,
                                                 dpm_creator_identify=user_identify)
        else:
            self.message = "用户未登录"
            self.signal = 2

        return Response({'message': self.message, 'signal': self.signal})

    def nameCheck(self, dpm_name):
        try:
            dpm = Department.objects.get(dpm_name=dpm_name)
        except Department.DoesNotExist:
            return True
        else:
            self.message = "角色已经存在"
            self.signal = 1
            return False


class DepartmentUpdateView(APIView):
    def __init__(self, **kwargs):
        super(DepartmentUpdateView, self).__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data['id']
        dpm_remarks = data['dpm_remarks']
        dpm_name = data['dpm_name']
        # dpm_status = data['dpm_status']
        if self.nameCheck(dpm_name, id):
            try:
                models.Department.objects.filter(id=id).update(dpm_name=dpm_name, dpm_remarks=dpm_remarks)
            except:
                self.message = "更新失败"
                self.signal = 1

        return Response({'message': self.message, 'signal': self.signal})

    def nameCheck(self, name, id):
        try:
            dpm = Department.objects.get(~Q(id=id), dpm_name=name)
        except Department.DoesNotExist:
            return True
        else:
            self.message = "部门名字已经存在"
            self.signal = 2
            return False


class DepartmentStatusView(APIView):
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data["id"]
        dpm_status = data['dpm_status']
        # dpm_identify = data['dpm_identify']
        dpm = Department.objects.filter(id=id)
        if dpm:
            dpm.update(dpm_status=dpm_status)
            return Response({"message": "状态更改成功", "signal": 0})
        else:
            return Response({"message": "未查询到部门,状态更改失败"})


class BrandsView(APIView):
    """品牌"""

    def get(self, request):
        brands = Brand.objects.all()
        if brands:
            brands_serializer = BrandSerializer(brands, many=True)
            return Response({"brands": brands_serializer.data})
        else:
            return Response({"message": "未查询到信息"})


class BrandAddView(APIView):
    """新增品牌"""

    def __init__(self, **kwargs):
        super(BrandAddView, self).__init__(**kwargs)
        self.message = "添加成功"
        self.signal = 0
        self.user_now_name = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_identify']
        user_now = UserNow.objects.get(user_iden=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
        brand_name = data['brand_name']
        brand_description = data['brand_description']
        if self.nameCheck(brand_name):
            Brand.objects.create(brand_name=brand_name, brand_status=0, brand_description=brand_description,
                                 brand_creator=self.user_now_name, brand_creator_identify=user_identify)
        return Response({'message': self.message, 'signal': self.signal})

    def nameCheck(self, name):
        try:
            brand = Brand.objects.get(brand_name=name)
        except Brand.DoesNotExist:
            return True
        else:
            self.message = "品牌已经存在"
            self.signal = 1
            return False


class BrandUpdateView(APIView):
    """更新品牌信息"""

    def __init__(self, **kwargs):
        super(BrandUpdateView, self).__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data['id']
        brand_name = data['brand_name']
        brand_description = data['brand_description']
        # brand_status = data['brand_status']
        # brand_creator = data['brand_creator']
        if self.nameCheck(brand_name, id):
            try:
                Brand.objects.filter(id=id).update(brand_name=brand_name, brand_description=brand_description, )
            except:
                self.message = "更新失败"
                self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})

    def nameCheck(self, name, id):
        try:
            brand = Brand.objects.get(~Q(id=id), brand_name=name)
        except Brand.DoesNotExist:
            return True
        else:
            self.message = "品牌已经存在"
            self.signal = 2
            return False


class BrandStatusView(APIView):
    """状态变更"""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data["id"]
        brand_status = data['brand_status']
        brand = Brand.objects.filter(id=id)
        if brand:
            brand.update(brand_status=brand_status)
            return Response({"message": "状态更改成功", "signal": 0})
        else:
            return Response({"message": "未查询到品牌,状态更改失败"})


class TotalWareHousesView(APIView):
    """仓库接口"""

    def get(self, request):
        max_id = TotalWareHouse.objects.all().aggregate(Max('total_identify'))['total_identify__max']
        totalWareHouses = TotalWareHouse.objects.all()
        if totalWareHouses:
            totalWareHouses_serializer = TotalWareHouseSerializer(totalWareHouses, many=True)
            return Response({"max_identify": max_id, "totalWareHouses": totalWareHouses_serializer.data})
        else:
            return Response({"message": "未查询到信息"})


class TotalWareHouseNewView(APIView):
    """"""

    def get(self, request):
        brands = Brand.objects.filter(brand_status=1).values_list('brand_name', flat=True)
        organizations = {}
        centers = {}
        areas_list = Area.objects.filter(area_status=1).values_list('area_name', flat=True)
        for area_name in areas_list:
            organization = models.Organization.objects.filter(area_name=area_name, orga_status=1).values_list(
                'org_name', flat=True)
            center = Center.objects.filter(area_name=area_name, center_status=1).values_list('center_name', flat=True)
            organizations[area_name] = organization
            centers[area_name] = center
        return Response({"brands": brands, "organizations": organizations, "centers": centers, "areas": areas_list})


class TotalWareHouseAddView(APIView):
    """
    这里绑定组织通过area_name和org_name再绑定
    可以优化为传入前端org_identify ，传回的时候传identify
    """

    def __init__(self, **kwargs):
        super(TotalWareHouseAddView, self).__init__(**kwargs)
        self.message = "添加成功"
        self.signal = 0
        self.user_now_name = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_identify']
        user_now = models.UserNow.objects.get(user_iden=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name

        total_identify = data['total_identify']
        total_name = data['total_name']
        area_name = data['area_name']
        org_name = data['org_name']
        brand_name = data['brand_name']
        total_belong_center = data['total_belong_center']
        try:
            total_belong_center_identify = models.Center.objects.get(center_name=total_belong_center, area_name=area_name)
        except models.Center.DoesNotExist:
            total_belong_center_identify = ""
        else:
            total_belong_center_identify = total_belong_center_identify.id

        total_remarks = data['total_remarks']

        organization = Organization.objects.get(area_name=area_name, org_name=org_name)
        if self.idCheck(total_identify):
            TotalWareHouse.objects.create(total_identify=total_identify, total_name=total_name, total_belong_center=total_belong_center, total_belong_center_identify=total_belong_center_identify, brand_name=brand_name, organization=organization, total_remarks=total_remarks, total_status=0, total_creator=self.user_now_name, total_creator_iden=user_identify)
        return Response({'message': self.message, 'signal': self.signal})

    def idCheck(self, total_identify):
        try:
            user = models.TotalWareHouse.objects.get(total_identify=total_identify)
        except models.TotalWareHouse.DoesNotExist:
            return True
        else:
            self.message = "仓库id已存在"
            self.signal = 1
            return False


class TotalWareHouseUpdateView(APIView):
    """更新"""

    def __init__(self, **kwargs):
        super(TotalWareHouseUpdateView, self).__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data['id']
        total_identify = data['total_identify']
        total_name = data['total_name']
        brand_name = data['brand_name']
        total_remarks = data['total_remarks']
        if self.idCheck(total_identify, id):
            try:
                TotalWareHouse.objects.filter(total_identify=total_identify).update(total_name=total_name, brand_name=brand_name, total_remarks=total_remarks)
            except:
                self.message = "更新失败"
                self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})

    def idCheck(self, total_identify, id):
        try:
            warehouse = TotalWareHouse.objects.get(~Q(id=id), total_identify=total_identify)
        except TotalWareHouse.DoesNotExist:
            return True
        else:
            self.message = "仓库id已存在"
            self.signal = 1
            return False


class TotalWareHouseStatusView(APIView):
    """状态变更"""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data["id"]
        total_status = data['total_status']
        total = TotalWareHouse.objects.filter(id=id)
        if total:
            total.update(total_status=total_status)
            return Response({"message": "状态更改成功", "signal": 0})
        else:
            return Response({"message": "未查询到仓库,状态更改失败"})


class CentersView(APIView):
    """中心接口"""

    def get(self, request):
        centers = Center.objects.all()
        if centers:
            centers_serializer = CenterSerializer(centers, many=True)
            return Response({"centers": centers_serializer.data})
        else:
            return Response({"message": "未查询到信息"})


class CenterNewView(APIView):
    """获取"""

    def get(self, request):
        areas = Area.objects.filter(area_status=1).values_list('area_name', flat=True)
        return Response({"areas": areas})


class CenterAddView(APIView):
    """新增"""

    def __init__(self, **kwargs):
        super(CenterAddView, self).__init__(**kwargs)
        self.message = "添加成功"
        self.signal = 0
        self.user_now_name = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_identify']
        user_now = models.UserNow.objects.get(user_identify=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
        # center_iden = data['center_iden']
        center_name = data['center_name']
        area_name = data['area_name']
        center_remarks = data['center_remarks']
        if self.isExist(center_name, area_name):
            Center.objects.create(center_name=center_name, area_name=area_name, center_remarks=center_remarks,
                                  center_status=0, center_creator=self.user_now_name, center_creator_iden=user_identify)
            logger.info('中心创建')
        return Response({'message': self.message, 'signal': self.signal})

    def isExist(self, center_name, area_name):
        try:
            center = Center.objects.get(center_name=center_name, area_name=area_name)
        except Center.DoesNotExist:
            logger.info('中心不存在')
            return True
        else:
            self.message = "中心名字和区域重复"
            self.signal = 1
            return False


class CenterUpdateView(APIView):
    """更新"""

    def __init__(self, **kwargs):
        super(CenterUpdateView, self).__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data['id']
        center_name = data['center_name']
        area_name = data['area_name']
        center_remarks = data['center_remarks']
        # center_creator = data['center_creator']
        if self.isExist(center_name, area_name, id):
            try:
                Center.objects.filter(id=id).update(center_name=center_name, center_remarks=center_remarks)
            except:
                self.message = "更新失败"
                self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})

    def isExist(self, center_name, area_name, id):
        try:
            center = Center.objects.get(~Q(id=id), center_name=center_name, area_name=area_name)
        except Center.DoesNotExist:
            return True
        else:
            self.message = "中心名字和区域重复"
            self.signal = 1
            return False


class CenterStatusView(APIView):
    """状态变更"""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data["id"]
        center_status = data['center_status']
        center = Center.objects.filter(id=id)
        if center:
            center.update(center_status=center_status)
            return Response({"message": "状态更改成功", "signal": 0})
        else:
            return Response({"message": "未查询到中心,状态更改失败"})


class CenterWareHousesView(APIView):
    """中心仓库接口"""

    def get(self, request):
        center_whs = CenterWareHouse.objects.all()
        if center_whs:
            center_whs_serializer = CenterWareHouseSerializer(center_whs, many=True)
            return Response({"centerWareHouses": center_whs_serializer.data})


class CenterWareHouseNewView(APIView):
    """获取中心仓"""

    def get(self, request):
        brands = Brand.objects.filter(brand_status=1).values_list('brand_name', flat=True)
        organizations = {}
        areas_list = Area.objects.filter(area_status=1).values_list('area_name', flat=True)
        for area_name in areas_list:
            org_center = []
            organization = Organization.objects.filter(area_name=area_name, orga_status=1).values_list('org_name', flat=True)
            center = Center.objects.filter(area_name=area_name, center_status=1).values_list('center_name', flat=True)
            org_center.append(organization)
            org_center.append(center)
            organizations[area_name] = org_center
        return Response({"brands": brands, "organizations": organizations})


class CenterWareHouseAddView(APIView):
    """新增"""

    def __init__(self, **kwargs):
        super(CenterWareHouseAddView, self).__init__(**kwargs)
        self.message = "添加成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        center_wh_identify = data['center_wh_identify']
        center_wh_name = data['center_wh_name']
        area_name = data['area_name']
        org_name = data['org_name']
        center_name = data['center_name']
        brand_name = data['brand_name']
        center_wh_remarks = data['center_wh_remarks']
        center_wh_status = data['center_wh_status']
        center_wh_creator = data['center_wh_creator']
        organization = Organization.objects.get(area_name=area_name, org_name=org_name)
        center = Center.objects.get(center_name=center_name)
        CenterWareHouse.objects.create(center_wh_identify=center_wh_identify, center_wh_name=center_wh_name,
                                       organization=organization, center=center, brand_name=brand_name,
                                       center_wh_remarks=center_wh_remarks, center_wh_status=center_wh_status,
                                       center_wh_creator=center_wh_creator)
        return Response({'message': self.message, 'signal': self.signal})


class CenterWareHouseUpdateView(APIView):
    """更新"""

    def __init__(self, **kwargs):
        super(CenterWareHouseUpdateView, self).__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        center_wh_identify = data['center_wh_identify']
        center_wh_remarks = data['center_wh_remarks']
        center_wh_status = data['center_wh_status']
        try:
            CenterWareHouse.objects.filter(center_wh_identify=center_wh_identify, ).update(
                center_wh_remarks=center_wh_remarks, center_wh_status=center_wh_status, )
        except:
            self.message = "更新失败"
            self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})


class SuppliersView(APIView):
    """供应商接口"""

    def get(self, request):
        max_id = Supplier.objects.all().aggregate(Max('supply_identify'))['supply_identify__max']
        suppliers = Supplier.objects.all()
        if suppliers:
            suppliers_serializer = SupplierSerializer(suppliers, many=True)
            return Response({"max_identify": max_id, "suppliers": suppliers_serializer.data})
        else:
            return Response({"message": "未查询到信息"})


class SupplierAddView(APIView):
    """新增供应商"""

    def __init__(self, **kwargs):
        super(SupplierAddView, self).__init__(**kwargs)
        self.message = "添加成功"
        self.signal = 0
        self.user_now_name = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_identify']
        user_now = models.UserNow.objects.get(user_iden=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
        max_id = Supplier.objects.all().aggregate(Max('supply_identify'))['supply_identify__max']
        if max_id:
            supply_identify = str(int(max_id) + 1).zfill(5)
        else:
            supply_identify = "0100001"
        supply_name = data['supply_name']
        supply_type = data['supply_type']
        supply_remarks = data['supply_remarks']
        Supplier.objects.create(supply_identify=supply_identify, supply_name=supply_name, supply_type=supply_type, supply_remarks=supply_remarks, supply_creator=self.user_now_name, supply_creator_iden=user_identify)
        return Response({'message': self.message, 'signal': self.signal})


class SupplierUpdateView(APIView):
    """更新"""

    def __init__(self, **kwargs):
        super(SupplierUpdateView, self).__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data['id']
        supply_identify = data['supply_identify']
        supply_name = data['supply_name']
        supply_type = data['supply_type']
        supply_remarks = data['supply_remarks']
        supply_status = data['supply_status']
        supply_creator = data['supply_creator']
        try:
            Supplier.objects.filter(supply_identify=supply_identify).update(supply_name=supply_name, supply_type=supply_type, supply_remarks=supply_remarks)
        except:
            self.message = "更新失败"
            self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})


class SupplierStatusView(APIView):
    """状态更新"""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        supply_status = data['supply_status']
        supply_identify = data['supply_identify']
        supplier = models.Supplier.objects.filter(supply_identify=supply_identify)
        if supplier:
            supplier.update(supply_status=supply_status)
            return Response({"message": "状态更改成功", "signal": 0})
        else:
            return Response({"message": "未查询到供应商,状态更改失败"})


class MeasuresView(APIView):
    """"""

    def get(self, request):
        max_id = Measure.objects.all().aggregate(Max('measure_identify'))['measure_identify__max']
        measure = Measure.objects.all()
        if measure:
            measure_serializer = measureerializer(measure, many=True)
            logger.info(measure_serializer.data)
            # print(measure_serializer.data)
            return Response({"max_identify": max_id, "measure": measure_serializer.data})
        else:
            return Response({"message": "未查询到信息"})


class MeasureAddView(APIView):

    def __init__(self, **kwargs):
        super(MeasureAddView, self).__init__(**kwargs)
        self.message = "添加成功"
        self.signal = 0
        self.user_now_name = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_identify']
        user_now = UserNow.objects.get(user_iden=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name

        measure_identify = data['measure_identify']
        measure_name = data['measure_name']
        measure_dimension = data['measure_dimension']

        if self.idCheck(measure_identify):
            if self.nameCheck(measure_name):
                Measure.objects.create(measure_identify=measure_identify, measure_name=measure_name,
                                               measure_dimension=measure_dimension, measure_status=0,
                                               measure_creator=self.user_now_name,
                                               measure_creator_iden=user_identify)

        return Response({'message': self.message, 'signal': self.signal})

    def idCheck(self, measure_identify):
        try:
            measure = Measure.objects.get(measure_identify=measure_identify)
        except Measure.DoesNotExist:
            return True
        else:
            self.message = "计量单位id已存在"
            self.signal = 1
            return False

    def nameCheck(self, measure_name):
        try:
            measure = Measure.objects.get(measure_name=measure_name)
        except Measure.DoesNotExist:
            return True
        else:
            self.message = "计量单位名字已存在"
            self.signal = 2
            return False


class MeasureUpdateView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data['id']
        measure_identify = data['measure_identify']
        measure_name = data['measure_name']
        measure_dimension = data['measure_dimension']

        if self.idCheck(measure_identify, id):
            try:
                Measure.objects.filter(id=id).update(measure_name=measure_name,
                                                             measure_dimension=measure_dimension)
            except:
                self.message = "更新失败"
                self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})

    def idCheck(self, measure_identify, id):
        try:
            measure = Measure.objects.get(~Q(id=id), measure_identify=measure_identify)
        except Measure.DoesNotExist:
            return True
        else:
            self.message = "计量单位id已存在"
            self.signal = 1
            return False


class MeasureStatusView(APIView):
    """"""
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        measure_status = data['measure_status']
        id = data["id"]
        measure = Measure.objects.filter(id=id)
        if measure:
            measure.update(measure_status=measure_status)
            return Response({"message": "状态更改成功", "signal": 0})
        else:
            return Response({"message": "未查询到计量单位,状态更改失败"})


class MaterialTypesView(APIView):
    """物料类别"""

    def get(self, request):
        max_id = MaterialType.objects.all().aggregate(Max('type_identify'))['type_identify__max']
        material_types = MaterialType.objects.all()
        if material_types:
            print(max_id)
            material_types_serializer = MaterialTypeSerializer(material_types, many=True)
            return Response({"max_identify": max_id, "material_types": material_types_serializer.data})
        else:
            return Response({"message": "未查询到信息"})


class MaterialTypeNewView(APIView):
    pass


class MaterialTypeAddView(APIView):

    def __init__(self, **kwargs):
        super(MaterialTypeAddView, self).__init__(**kwargs)
        self.message = "添加成功"
        self.signal = 0
        self.user_now_name = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_now_identify']
        user_now = UserNow.objects.get(user_idenify=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
        type_identify = data['type_identify']
        type_name = data['type_name']

        if self.idCheck(type_iden):
            MaterialType.objects.create(type_iden=type_iden, type_name=type_name, type_status=0, type_creator=self.user_now_name, type_creator_identify=user_identify)

        return Response({"message": self.message, "signal": self.signal})

    def idCheck(self, type_identify):
        try:
            measure = MaterialType.objects.get(type_identify=type_identify)
        except MaterialType.DoesNotExist:
            return True
        else:
            self.message = "物料类别id已存在"
            self.signal = 1
            return False


class MaterialTypeUpdateView(APIView):
    """"""

    def __init__(self, **kwargs):
        super(MaterialTypeUpdateView, self).__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))

        id = data['id']
        type_identify = data['type_identify']
        type_name = data['type_name']

        try:
            MaterialType.objects.filter(id=id).update(type_name=type_name)
        except:
            self.message = "更新失败"
            self.signal = 1
        return Response({"message": self.message, "signal": self.signal})


class MaterialTypeStatusView(APIView):
    """"""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        type_status = data['type_status']
        id = data["id"]
        type = MaterialType.objects.filter(id=id)
        if type:
            type.update(type_status=type_status)
            return Response({"message": "状态更改成功", "signal": 0})
        else:
            return Response({"message": "未查询到物料类别,状态更改失败"})


class MaterialsView(APIView):
    """"""

    def get(self, request):
        materials = Material.objects.all()
        if materials:
            materials_serializer = MaterialSerializer(materials, many=True)
            return Response({"materials": materials_serializer.data})
        else:
            return Response({"message": "未查询到信息"})


class MaterialNewView(APIView):
    """物料获取"""

    def get(self, request):
        """物料类别及其名字和最大流水号编码"""
        material_types = Material.objects.filter(type_status=1).values_list('type_identify', 'type_name')
        measure = models.Meterage.objects.filter(measure_status=1).values_list('measure_dimension',   'measure_identify', 'measure_name')
        return Response({"material_types": material_types, "measure": measure})


class MaterialAddView(APIView):
    """"""

    def __init__(self, **kwargs):
        super(MaterialAddView, self).__init__(**kwargs)
        self.message = "添加成功"
        self.signal = 0
        self.user_now_name = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_now_identify']
        user_now = UserNow.objects.get(user_identify=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name

        material_name = data['material_name']
        material_type_identify = data['material_type_identify']
        material_specification = data['material_specification']
        material_model = data['material_model']
        measure_name = data['measure_name']
        material_attr = data['material_attr']

        max_id = Material.objects.filter(material_type_identify=material_type_identify).aggregate(Max('material_identify'))['material_identify__max']
        if max_id:
            material_identify = str(int(max_id) + 1)
        else:
            material_identify = material_type_identify + "00001"
        Material.objects.create(material_identify=material_identify, material_name=material_name,
                                       material_type_identify=material_type_identify,
                                       material_specification=material_specification,
                                       material_model=material_model, measure_name=measure_name,
                                       material_attr=material_attr, material_status=0,
                                       material_creator=self.user_now_name,
                                       material_creator_identify=user_identify)
        return Response({'message': self.message, 'signal': self.signal})


class MaterialUpdateView(APIView):
    """"""

    def __init__(self, **kwargs):
        super(MaterialUpdateView, self).__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data['id']
        material_identify = data['material_identify']
        material_name = data['material_name']
        material_specification = data['material_specification']
        material_model = data['material_model']
        measure_name = data['measure_name']
        material_attr = data['material_attr']

        try:
            Material.objects.filter(id=id).update(material_name=material_name, material_specification=material_specification, material_model=material_model,   measure_name=measure_name, material_attr=material_attr, )
        except:
            self.message = "更新失败"
            self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})


class MaterialStatusView(APIView):
    """"""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data["id"]
        material_status = data['material_status']
        material = Material.objects.filter(id=id)
        if material:
            material.update(material_status=material_status)
            return Response({"message": "状态更改成功", "signal": 0})
        else:
            return Response({"message": "未查询到物料,状态更改失败"})
