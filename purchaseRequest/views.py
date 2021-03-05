import traceback
import datetime
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, Max
from django.utils import timezone
from django.shortcuts import render, redirect
from ..base.models import UserNow, UserProfile, Organization, Supplier, Material, Department

from . import models
from .serializer import PurchaseRequestSerializer,  PurchaseRequestDetailSerializer


logger = logging.getLogger(__name__)


class PurchaseRequestsView(APIView):
    """获取所有请购单"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_now_name = ""
        self.area_name = ""

    def post(self, request):
        """需要获取区域名字，用户编号"""
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_now_identify']
        user_now = UserNow.objects.get(user_iden=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name

        permission = data['permission']
        print(permission)
        # 判断是个人还是采购专员
        if permission == '1':
            prs = models.PurchaseRequest.objects.filter(~Q(pr_status=0), organization__area_name=self.area_name).all()
        elif permission == '2':
            prs = models.PurchaseRequest.objects.filter(pr_creator_identify=user_identify, organization__area_name=self.area_name).all()
        else:
            prs1 = models.PurchaseRequest.objects.filter(~Q(pr_status=0), organization__area_name=self.area_name).all()
            prs2 = models.PurchaseRequest.objects.filter(pr_creator_identify=user_identify, organization__area_name=self.area_name).all()
            prs = prs1 | prs2
        if prs:
            prs_serializer = PurchaseRequestSerializer(prs, many=True)
            return Response({"prs": prs_serializer.data, "signal": 0})
        else:
            return Response({"message": "未查询到信息"})


class PurchaseRequestNewView(APIView):
    """新建请购单"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_now_name = ""
        self.area_name = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_now_identify']
        user_now = UserNow.objects.get(user_iden=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name

        org_names = Organization.objects.filter(area_name=self.area_name, org_status=1).values_list('id', 'org_name')
        dpms = Department.objects.filter(dpm_status=1).values_list('id', 'dpm_name', 'dpm_center')
        try:
            pr_identify = data['pr_identify']
            org_name = data['org_name']
        except:
            return Response({"org_names": org_names, "dpms": dpms, "signal": 0})
        else:
            prds = models.PurchaseRequestDetail.objects.filter(purchase_request__pr_identify=pr_identify)
            prds_serializers = PurchaseRequestDetailSerializer(prds, many=True)
            prds_present_num = []
            for prd in prds:
                material = prd.material
                prd_present_num = TotalStock.objects.filter(
                    totalwarehouse__organization__org_name=org_name,
                   totalwarehouse__organization__area_name=self.area_name,
                    material=material).aggregate( prd_present_num=Sum('ts_present_num'))['prd_present_num']
                if prd_present_num:
                    pass
                else:
                    prd_present_num = 0
                prds_present_num.append(prd_present_num)

            return Response({"org_names": org_names, 'dpms': dpms, "prds": prds_serializers.data, "prds_present_num": prds_present_num, "signal": 1})


# class PurchaseRequestUpdateView(APIView):
#     """只读取添加的数据，订单号自动生成，用于保存新增和编辑的订单 """
#
#     def post(self, request):
#         message_return = {}
#         data = json.loads(request.body.decode("utf-8"))
#         pr_status = data['pr_status']
#         area_name = data['area_name']
#         pr_identify = data['pr_identify']
#         pr = models.PurchaseRequest.objects.get(pr_identify=pr_identify)
#         prds = models.PurchaseRequestDetail.objects.filter(purchase_request=pr)
#         if prds:
#             prds_serializer = PurchaseRequestDetailSerializer(prds, many=True)
#             message_return["prds"] = prds_serializer.data
#         else:
#             message_return["prds"] = ""
#
#         if pr_status == 0:
#             org_names = Organization.objects.filter(area_name=area_name).values_list('org_name', flat=True)
#             message_return["organizations"] = org_names
#         else:
#             message_return["message"] = "请购单明细为空"
#         return Response({'message': message_return})


class PurchaseRequestUpdateView(APIView):
    """只读取添加的数据，订单号自动生成，用于保存新增和编辑的订单"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0
        self.user_now_name = ""
        self.area_name = ""
        self.pr_new_identify = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_now_identify']
        user_now = UserNow.objects.get(user_iden=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name
        org_name = data['org_name']
        organization = Organization.objects.get(area_name=self.area_name, org_name=org_name)
        department_name = data['pr_department']
        pr_type = data['pr_type']
        pr_date = data['pr_date']
        pr_remarks = data['pr_remarks']
        print(pr_date)

        try:
            pr_identify = data['pr_identify']
        except:
            date_str = timezone.now().strftime("%Y-%m-%d")
            date = "".join(date_str.split("-"))
            pre_identify = "PR" + date
            max_id = models.PurchaseRequest.objects.all().aggregate(Max('pr_serial'))['pr_serial__max']
            if max_id:
                pr_serial = str(int(max_id) + 1).zfill(4)
            else:
                pr_serial = "0001"
            pr_new_identify = pre_identify + pr_serial
            self.pr_new_identify = pr_new_identify
            try:
                res = models.PurchaseRequest.objects.create(pr_identify=pr_new_identify, pr_serial=pr_serial,
                                                            organization=organization, pr_department=department_name,
                                                            pr_type=pr_type, pr_date=pr_date,
                                                            pr_remarks=pr_remarks,
                                                            pr_status=0, pr_creator=self.user_now_name,
                                                            pr_creator_identify=user_identify)
                if res:
                    self.message = "新建请购单成功"
                    self.signal = 0
                else:
                    self.message = "新建请购单失败"
                    self.signal = 1
            except:
                traceback.print_exc()
                self.message = "新建请购单失败"
                self.signal = 1
        else:
            pr = models.PurchaseRequest.objects.filter(pr_identify=pr_identify)
            if pr:
                if pr.update(organization=organization, pr_department=department_name, pr_type=pr_type, pr_date=pr_date, pr_remarks=pr_remarks):
                    pass
                else:
                    self.message = "更新失败"
                    self.signal = 1
            else:
                self.message = "更新失败"
                self.signal = 1
        return Response({"message": self.message, "signal": self.signal, "pr_new_identify": self.pr_new_identify})


class PurchaseRequestDetailSaveView(APIView):
    """"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "请购单详情保存成功"
        self.signal = 0

    def post(self, request):
        """需要获取物料详情信息(主要是identify和请购数量）"""
        data = json.loads(request.body.decode("utf-8"))
        prds = data['prds']
        pr_identify = data['pr_identify']
        models.PurchaseRequestDetail.objects.filter(purchase_request__pr_identify=pr_identify).delete()
        pr = models.PurchaseRequest.objects.get(pr_identify=pr_identify)
        print('prds')
        for prd in prds:
            prd_identify = prd['prd_identify']  # 物料编码
            # id = prd['prd_id']  # 物料id
            prd_num = prd['prd_num']  # 请购数量
            prd_present_num = prd['prd_present_num']  # 实际库存数量
            prd_remarks = prd['prd_remarks']
            material = Material.objects.get(material_iden=prd_identify)
            try:
                s = models.PurchaseRequestDetail.objects.create(purchase_request=pr, prd_num=prd_num,
                                                   material = material,
                                                   prd_used = 0,
                                                   prd_present_num=prd_present_num,
                                                   prd_remarks=prd_remarks)
                print(s)
                #     pass
                # else:
                #     self.message = "请购单详情保存失败"
                #     self.signal = 1
            except:
                traceback.print_exc()
                self.message = "请购单详情保存失败"
                self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})


class PurchaseRequestDetailSubmitView(APIView):
    """提交请购单详情"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "请购单提交成功"
        self.signal = 0

    def post(self, request):
        """提交后将草稿改为已审批，需要数据为"""
        data = json.loads(request.body.decode("utf-8"))
        pr_identify = data['pr_identify']
        try:
            if models.PurchaseRequest.objects.filter(pr_identify=pr_identify).update(pr_status=1):
                pass
            else:
                self.message = "请购单提交保存失败"
                self.signal = 1
        except:
            self.message = "请购单提交保存失败"
            self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})


class PurchaseRequestDetailNewView(APIView):
    """请购单详情"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_now_name = ""
        self.area_name = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_now_identify']
        user_now = UserNow.objects.get(user_identify=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name
        org_name = data['org_name']
        materials = Material.objects.filter(material_status=1).all()

        if materials:
            materials_serializer = MaterialSerializer(materials, many=True)
            prds_present_num = []
            for material in materials:
                prd_present_num = TotalStock.objects.filter(totalwarehouse__organization__org_name=org_name,
                                                            totalwarehouse__organization__area_name=self.area_name,
                                                            material=material).aggregate(prd_present_num=Sum('ts_present_num'))['prd_present_num']
                if prd_present_num:
                    pass
                else:
                    prd_present_num = 0
                prds_present_num.append(prd_present_num)

            return Response({"materials": materials_serializer.data, "prds_present_num": prds_present_num, "signal": 0})
        else:
            return Response({"message": "空空如也你不服？"})


# class PrdNewSaveView(APIView):
#     def post(self, request):
#         """
#         需要获取物料详情(iden ,现存量，请购量就可以了)，请购单编号
#         """
#         data = json.loads(request.body.decode("utf-8"))
#         pr_identify = data['pr_identify']
#         prds = data['prds']
#         for prd in prds:
#             prd_identify = prd['prd_identify']
#             # prd_num = prd['prd_num']
#             prd_present_num = prd['prd_present_num']
#             material = Material.objects.get(material_iden=prd_identify)
#             pr = models.PurchaseRequest.objects.get(pr_identify=pr_identify)
#             try:
#                 if models.PurchaseRequestDetail.objects.create(purchase_request=pr, material=material, prd_num=prd_present_num,
#                                                   prd_present_num=prd_present_num, prd_used=0):
#                     pass
#                 else:
#                     return Response({"message": "新建物料出现错误"})
#             except:
#                 return Response({"message": "新建物料出现错误"})
#
#         return Response({"message": "新建物料详情成功", "signal": 0})


class PurchaseRequestDeleteView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "删除请购单成功"
        self.signal = 0

    def post(self, request):
        """需要数据为请购单编号"""
        data = json.loads(request.body.decode("utf-8"))
        pr_identify = data['pr_identify']
        try:
            if models.PurchaseRequest.objects.filter(pr_identify=pr_identify).delete()[0]:
                pass
            else:
                self.message = "删除请购单失败"
                self.signal = 1
        except:
            self.message = "删除请购单失败"
            self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})


class PurchaseRequestCloseView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0
        self.user_now_name = ""
        self.area_name = ""
        self.pr_new_identify = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_now_identify']
        user_now = UserNow.objects.get(user_iden=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name

        pr_identify = data['pr_identify']
        pr_closerReason = data['pr_closerReason']
        try:
            if models.PurchaseRequest.objects.filter(pr_identify=pr_identify).update(pr_status=2, pr_closer=self.user_now_name,
                                                                             pr_closer_iden = user_identify,
                                                                             pr_closeReason=pr_closerReason):
                pass
            else:
                traceback.print_exc()
                self.message = "关闭请购单失败"
                self.signal = 1
        except:
            traceback.print_exc()
            self.message = "关闭请购单失败"
            self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})
