import json
import traceback
# import datetime
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, Max, Sum
from django.utils import timezone
# from django.shortcuts import render, redirect
from base.models import UserNow, Organization, Material, Department
from base.serializer import MaterialSerializer
from storeManage.models import TotalStock

from . import models
from .serializer import PurchaseRequestSerializer, PurchaseRequestDetailSerializer

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
            prqs = models.PurchaseRequest.objects.filter(~Q(prq_status=0), organization__area_name=self.area_name).all()
        elif permission == '2':
            prqs = models.PurchaseRequest.objects.filter(prq_creator_identify=user_identify,
                                                         organization__area_name=self.area_name).all()
        else:
            prqs1 = models.PurchaseRequest.objects.filter(~Q(prq_status=0),
                                                          organization__area_name=self.area_name).all()
            prqs2 = models.PurchaseRequest.objects.filter(prq_creator_identify=user_identify,
                                                          organization__area_name=self.area_name).all()
            prqs = prqs1 | prqs2
        if prqs:
            prqs_serializer = PurchaseRequestSerializer(prqs, many=True)
            return Response({"prqs": prqs_serializer.data, "signal": 0})
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
            prq_identify = data['prq_identify']
            org_name = data['org_name']
        except:
            return Response({"org_names": org_names, "dpms": dpms, "signal": 0})
        else:
            prqds = models.PurchaseRequestDetail.objects.filter(purchase_request__prq_identify=prq_identify)
            prqds_serializers = PurchaseRequestDetailSerializer(prqds, many=True)
            prqds_present_num = []
            for prqd in prqds:
                material = prqd.material
                prqd_present_num = TotalStock.objects.filter(
                    totalwarehouse__organization__org_name=org_name,
                    totalwarehouse__organization__area_name=self.area_name,
                    material=material).aggregate(prqd_present_num=Sum('ts_present_num'))['prqd_present_num']
                if prqd_present_num:
                    pass
                else:
                    prqd_present_num = 0
                prqds_present_num.append(prqd_present_num)

            return Response({"org_names": org_names, 'dpms': dpms, "prqds": prqds_serializers.data,
                             "prqds_present_num": prqds_present_num, "signal": 1})


# class PurchaseRequestUpdateView(APIView):
#     """只读取添加的数据，订单号自动生成，用于保存新增和编辑的订单 """
#
#     def post(self, request):
#         message_return = {}
#         data = json.loads(request.body.decode("utf-8"))
#         prq_status = data['prq_status']
#         area_name = data['area_name']
#         prq_identify = data['prq_identify']
#         prq = models.PurchaseRequest.objects.get(prq_identify=prq_identify)
#         prqds = models.PurchaseRequestDetail.objects.filter(purchase_request=prq)
#         if prqds:
#             prqds_serializer = PurchaseRequestDetailSerializer(prqds, many=True)
#             message_return["prqds"] = prqds_serializer.data
#         else:
#             message_return["prqds"] = ""
#
#         if prq_status == 0:
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
        self.prq_new_identify = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_now_identify']
        user_now = UserNow.objects.get(user_iden=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name
        org_name = data['org_name']
        organization = Organization.objects.get(area_name=self.area_name, org_name=org_name)
        department_name = data['prq_department']
        prq_type = data['prq_type']
        prq_date = data['prq_date']
        prq_remarks = data['prq_remarks']
        print(prq_date)

        try:
            prq_identify = data['prq_identify']
        except:
            date_str = timezone.now().strftime("%Y-%m-%d")
            date = "".join(date_str.split("-"))
            prqe_identify = "PR" + date
            max_id = models.PurchaseRequest.objects.all().aggregate(Max('prq_serial'))['prq_serial__max']
            if max_id:
                prq_serial = str(int(max_id) + 1).zfill(4)
            else:
                prq_serial = "0001"
            prq_new_identify = prqe_identify + prq_serial
            self.prq_new_identify = prq_new_identify
            try:
                res = models.PurchaseRequest.objects.create(prq_identify=prq_new_identify, prq_serial=prq_serial,
                                                            organization=organization, prq_department=department_name,
                                                            prq_type=prq_type, prq_date=prq_date,
                                                            prq_remarks=prq_remarks,
                                                            prq_status=0, prq_creator=self.user_now_name,
                                                            prq_creator_identify=user_identify)
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
            prq = models.PurchaseRequest.objects.filter(prq_identify=prq_identify)
            if prq:
                if prq.update(organization=organization, prq_department=department_name, prq_type=prq_type,
                              prq_date=prq_date, prq_remarks=prq_remarks):
                    pass
                else:
                    self.message = "更新失败"
                    self.signal = 1
            else:
                self.message = "更新失败"
                self.signal = 1
        return Response({"message": self.message, "signal": self.signal, "prq_new_identify": self.prq_new_identify})


class PurchaseRequestDetailSaveView(APIView):
    """"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "请购单详情保存成功"
        self.signal = 0

    def post(self, request):
        """需要获取物料详情信息(主要是identify和请购数量）"""
        data = json.loads(request.body.decode("utf-8"))
        prqds = data['prqds']
        prq_identify = data['prq_identify']
        models.PurchaseRequestDetail.objects.filter(purchase_request__prq_identify=prq_identify).delete()
        prq = models.PurchaseRequest.objects.get(prq_identify=prq_identify)
        print('prqds')
        for prqd in prqds:
            prqd_identify = prqd['prqd_identify']  # 物料编码
            # id = prqd['prqd_id']  # 物料id
            prqd_num = prqd['prqd_num']  # 请购数量
            prqd_present_num = prqd['prqd_present_num']  # 实际库存数量
            prqd_remarks = prqd['prqd_remarks']
            material = Material.objects.get(material_iden=prqd_identify)
            try:
                s = models.PurchaseRequestDetail.objects.create(purchase_request=prq, prqd_num=prqd_num,
                                                                material=material,
                                                                prqd_used=0,
                                                                prqd_present_num=prqd_present_num,
                                                                prqd_remarks=prqd_remarks)
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
        prq_identify = data['prq_identify']
        try:
            if models.PurchaseRequest.objects.filter(prq_identify=prq_identify).update(prq_status=1):
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
            prqds_present_num = []
            for material in materials:
                prqd_present_num = TotalStock.objects.filter(totalwarehouse__organization__org_name=org_name,
                                                             totalwarehouse__organization__area_name=self.area_name,
                                                             material=material).aggregate(
                    prqd_present_num=Sum('ts_present_num'))['prqd_present_num']
                if prqd_present_num:
                    pass
                else:
                    prqd_present_num = 0
                prqds_present_num.append(prqd_present_num)

            return Response(
                {"materials": materials_serializer.data, "prqds_present_num": prqds_present_num, "signal": 0})
        else:
            return Response({"message": "空空如也你不服？"})


# class PrdNewSaveView(APIView):
#     def post(self, request):
#         """
#         需要获取物料详情(iden ,现存量，请购量就可以了)，请购单编号
#         """
#         data = json.loads(request.body.decode("utf-8"))
#         prq_identify = data['prq_identify']
#         prqds = data['prqds']
#         for prqd in prqds:
#             prqd_identify = prqd['prqd_identify']
#             # prqd_num = prqd['prqd_num']
#             prqd_present_num = prqd['prqd_present_num']
#             material = Material.objects.get(material_iden=prqd_identify)
#             prq = models.PurchaseRequest.objects.get(prq_identify=prq_identify)
#             try:
#                 if models.PurchaseRequestDetail.objects.create(purchase_request=prq, material=material, prqd_num=prqd_present_num,
#                                                   prqd_present_num=prqd_present_num, prqd_used=0):
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
        prq_identify = data['prq_identify']
        try:
            if models.PurchaseRequest.objects.filter(prq_identify=prq_identify).delete()[0]:
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
        self.prq_new_identify = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_now_identify']
        user_now = UserNow.objects.get(user_iden=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name

        prq_identify = data['prq_identify']
        prq_closerReason = data['prq_closerReason']
        try:
            if models.PurchaseRequest.objects.filter(prq_identify=prq_identify).update(prq_status=2,
                                                                                       prq_closer=self.user_now_name,
                                                                                       prq_closer_iden=user_identify,
                                                                                       prq_closeReason=prq_closerReason):
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
