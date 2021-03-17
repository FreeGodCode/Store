import json
import traceback

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
# from django.shortcuts import render, redirect
from django.db.models import Q, Max

from base.models import UserNow, Department, Organization, TotalWareHouse, Material
from storeManage.models import TotalStock
from . import models
from .serializer import TransferRequestSerializer, TransferSerializer, TransferRequestDetailSerializer, \
    TransferDetailSerializer, TransferRequestDetailToTransferDetailSerializer


class TransferRequestsView(APIView):
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

        permission = data['permission']
        print(permission)
        if permission == '1':
            strs = models.TransferRequest.objects.filter(~Q(str_status=0), organization__area_name=self.area_name).all()
        elif permission == '2':
            strs = models.TransferRequest.objects.filter(str_creator_identify=user_identify, organization__area_name=self.area_name).all()
        else:
            strs1 = models.TransferRequest.objects.filter(~Q(str_status=0), organization__area_name=self.area_name).all()
            strs2 = models.TransferRequest.objects.filter(str_creator_identify=user_identify, organization__area_name=self.area_name).all()
            strs = strs1 | strs2
        if strs:
            strs_serializer = TransferRequestSerializer(strs, many=True)
            return Response({"strs": strs_serializer.data, "signal": 0})
        else:
            return Response({"message": "未查询到信息"})


class TransferRequestNewView(APIView):
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

        org_ware_houses = {}
        organizations = Organization.objects.filter(area_name=self.area_name, org_status=1)
        for organization in organizations:
            org_name = organization.org_name
            out_ware_houses = TotalWareHouse.objects.filter(organization=organization, total_status=1).values_list("total_name", flat=True)
            org_ware_houses[org_name] = out_ware_houses

        dpms = Department.objects.filter(dpm_status=1).values_list('id', 'dpm_name', 'dpm_center')

        try:
            str_identify = data['str_identify']
            org_name = data['org_name']
            str_from_house = data['str_from_house']
        except:
            return Response({"org_ware_houses": org_ware_houses, "dpms": dpms, 'signal': 0})
        else:
            trds = models.TransferRequestDetail.objects.filter(transfer_request__str_identify=str_identify)
            trds_serializer = TransferRequestDetailSerializer(trds, many=True)
            trds_present_num = []
            for trd in trds:
                material = trd.material
                try:
                    trd_present_num = TotalStock.objects.get(totalwarehouse__organization__org_name=org_name,
                                                             totalwarehouse__organization__area_name=self.area_name,
                                                             totalwarehouse__total_name=str_from_house,
                                                             material=material).ts_present_num
                except:
                    trd_present_num = 0
                trds_present_num.append(trd_present_num)
            return Response({"org_ware_houses": org_ware_houses, "dpms": dpms, "trds": trds_serializer.data,
                             "trds_present_num": trds_present_num, "signal": 1})


class TransferRequestUpdateView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0
        self.user_now_name = ""
        self.area_name = ""
        self.str_new_identify = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_now_identify']
        user_now = UserNow.objects.get(user_identify=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name

        org_name = data['org_name']
        organization = Organization.objects.get(org_name=org_name, area_name=self.area_name)
        str_to_house = data['str_to_house']
        str_from_house = data['str_from_house']
        str_department = data['str_department']
        str_date = data['str_date']

        try:
            str_identify = data['str_identify']

        except:
            date_str = timezone.now().strftime("%Y-%m-%d")
            date = "".join(date_str.split("-"))
            pre_identify = "STR" + date
            max_id = models.TransferRequest.objects.all().aggregate(Max('str_serial'))['str_serial__max']
            if max_id:
                str_serial = str(int(max_id) + 1).zfill(4)
            else:
                str_serial = "0001"
            str_new_identify = pre_identify + str_serial
            self.str_new_identify = str_new_identify
            try:
                if models.TransferRequest.objects.create(str_identify=str_new_identify, str_serial=str_serial,
                                                         organization=organization, str_to_house=str_to_house,
                                                         str_from_house=str_from_house, str_date=str_date,
                                                         str_department=str_department, str_status=0,
                                                         str_creator=self.user_now_name,
                                                         str_creator_identify=user_identify):
                    self.message = "新建转库申请单成功"
                    self.signal = 0
                else:
                    self.message = "新建转库申请单失败"
                    self.signal = 1
            except:
                traceback.print_exc()
                self.message = "新建转库申请单失败"
                self.signal = 1
        else:
            Str = models.TransferRequest.objects.filter(str_identify=str_identify)
            if Str:
                if Str.update(organization=organization, str_department=str_department, str_to_house=str_to_house, str_date=str_date):
                    pass
                else:
                    self.message = "更新失败"
                    self.signal = 1
            else:
                self.message = "更新失败"
                self.signal = 1
        return Response({"message": self.message, "signal": self.signal, "str_new_identify": self.str_new_identify})


class TransferRequestDetailSaveView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "转库申请单详情保存成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        str_identify = data['str_identify']
        trds = data['trds']
        models.TransferRequestDetail.objects.filter(transfer_request__str_identify=str_identify).delete()

        str = models.TransferRequest.objects.get(str_identify=str_identify)
        for trd in trds:
            trd_identify = trd['trd_identify']
            material = Material.objects.get(material_identify=trd_identify)
            trd_num = trd['trd_num']
            trd_present_num = trd['trd_present_num']
            trd_remarks = trd['trd_remarks']

            try:
                if models.TransferRequestDetail.objects.create(transfer_request=str, material=material, trd_num=trd_num,
                                                  trd_present_num=trd_present_num, trd_used=0, trd_remarks=trd_remarks):
                    pass
                else:
                    self.message = "转库申请单详情保存失败"
                    self.signal = 1
            except:
                traceback.print_exc()
                self.message = "转库申请单详情保存失败"
                self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})


class TransferRequestDetailSubmitView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "转库申请单详情提交成功"
        self.signal = 0

    def post(self, request):
        """
        提交后将草稿改为已审批
        """
        data = json.loads(request.body.decode("utf-8"))
        str_identify = data['str_identify']

        try:
            if models.TransferRequest.objects.filter(str_identify=str_identify).update(str_status=1):
                pass
            else:
                self.message = "转库申请单详情提交保存失败"
                self.signal = 1
        except:
            self.message = "转库申请单详情提交保存失败"
            self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})


class TransferRequestDetailNewView(APIView):
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
        str_from_house = data['str_from_house']

        total_ware_house = TotalWareHouse.objects.filter(organization__org_name=org_name,
                                                         organization__area_name=self.area_name,
                                                         total_name=str_from_house).first()
        print(total_ware_house)
        total_stocks = total_ware_house.total_ware_house_ts.all()
        if total_stocks:
            total_stocks_serializer = TotalStockToTransferRequestSerializer(total_stocks, many=True)
            return Response({"materials": total_stocks_serializer.data})
        else:
            return Response({"message": "仓库空空如也"})


class TransferRequestDeleteView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "删除转库申请单成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        str_identify = data['str_identify']

        try:
            if models.TransferRequest.objects.filter(str_identify=str_identify).delete()[0]:
                pass
            else:
                self.message = "删除转库申请单失败"
                self.signal = 1
        except:
            self.message = "删除转库申请单失败"
            self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})


class TransfersView(APIView):
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

        permission = data['permission']
        print(permission)

        if permission == '1':
            sts = models.Transfer.objects.filter(~Q(st_status=0), organization__area_name=self.area_name).all()
        elif permission == '2':
            sts = models.Transfer.objects.filter(st_creator_identify=user_identify, organization__area_name=self.area_name).all()
        else:
            sts1 = models.Transfer.objects.filter(~Q(st_status=0), organization__area_name=self.area_name).all()
            sts2 = models.Transfer.objects.filter(st_creator_identify=user_identify, organization__area_name=self.area_name).all()
            sts = sts1 | sts2
        if sts:
            sts_serializer = TransferSerializer(sts, many=True)
            return Response({"strs": sts_serializer.data, "signal": 0})
        else:
            return Response({"message": "未查询到信息"})


class TransferNewView(APIView):
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
        org_ware_houses = {}
        organizations = Organization.objects.filter(area_name=self.area_name, org_status=1)

        for organization in organizations:
            org_name = organization.org_name
            out_ware_houses = TotalWareHouse.objects.filter(organization=organization, total_status=1).values_list("total_name", flat=True)
            org_ware_houses[org_name] = out_ware_houses
        try:
            st_identify = data['st_identify']
            org_name = data['org_name']
            st_from_house = data['st_from_house']
            # st_to_house = data['st_to_house']
        except:
            return Response({"org_ware_houses": org_ware_houses, 'signal': 0})
        else:
            tds = models.Transfer.objects.filter(transfer__st_identify=st_identify)
            tds_serializer = TransferDetailSerializer(tds, many=True)
            tds_present_num = []
            for td in tds:
                material = td.material
                try:
                    td_present_num = TotalStock.objects.get(totalwarehouse__organization__org_name=org_name,
                                                            totalwarehouse__organization__area_name=self.area_name,
                                                            totalwarehouse__total_name=st_from_house,
                                                            material=material).ts_present_num
                except:
                    td_present_num = 0
                tds_present_num.append(td_present_num)
            return Response({"org_ware_houses": org_ware_houses, "tds": tds_serializer.data, "tds_present_num": tds_present_num, "signal": 1})


class TransferRequestDetailNewByTrView(APIView):
    """转库单明细添加(根据转库申请单添加)"""

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
        st_from_house = data['st_from_house']
        st_to_house = data['st_to_house']

        trds = models.TrDetail.objects.filter(transfer_request__organization__area_name=self.area_name,
                                              transfer_request__organization__org_name=org_name,
                                              transfer_request__str_to_house=st_to_house,
                                              transfer_request__str_from_house=st_from_house,
                                              trd_used=0).all()
        if trds:
            tds_present_num = []
            for trd in trds:
                material = trd.material
                try:
                    td_present_num = TotalStock.objects.get(totalwarehouse__organization__org_name=org_name,
                                                            totalwarehouse__organization__area_name=self.area_name,
                                                            totalwarehouse__total_name=st_from_house,
                                                            material=material).ts_present_num
                except:
                    td_present_num = 0
                tds_present_num.append(td_present_num)
            tds_serializer = TrDToStDSerializer(trds, many=True)
            return Response({"tds": tds_serializer.data, "tds_present_num": tds_present_num})
        else:
            return Response({"message": "转库申请单没有数据"})


class TrdNewView(APIView):
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
        st_from_house = data['st_from_house']
        # st_to_house = data['st_to_house']

        total_stocks = TotalStock.objects.filter(totalwarehouse__total_name=st_from_house,
                                                 totalwarehouse__organization__area_name=self.area_name,
                                                 totalwarehouse__organization__org_name=org_name).all()
        if total_stocks:
            total_stocks_serializer = TotalStockToTdSerializer(total_stocks, many=True)
            return Response({"tds": total_stocks_serializer.data})
        else:
            return Response({"message": "快乐是你们的,我什么都没有"})


class TransferUpdateView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0
        self.user_now_name = ""
        self.area_name = ""
        self.st_new_identify = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_now_identify']
        user_now = UserNow.objects.get(user_identify=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name
        org_name = data['org_name']
        organization = Organization.objects.get(area_name=self.area_name, org_name=org_name)
        st_to_house = data['st_to_house']
        st_from_house = data['st_from_house']
        st_date = data['st_date']

        try:
            st_identify = data['st_identify']
        except:
            date_str = timezone.now().strftime("%Y-%m-%d")
            date = "".join(date_str.split("-"))
            pre_identify = "ST" + date
            max_id = models.Transfer.objects.all().aggregate(Max('st_serial'))['st_serial__max']
            if max_id:
                st_serial = str(int(max_id) + 1).zfill(4)
            else:
                st_serial = "0001"
            st_new_identify = pre_identify + st_serial
            self.st_new_identify = st_new_identify
            try:
                if models.Transfer.objects.create(st_identify=st_new_identify, st_serial=st_serial, organization=organization,
                                                  st_to_house=st_to_house, st_from_house=st_from_house, st_date=st_date,
                                                  st_status=0, st_creator=self.user_now_name,
                                                  st_creator_identify=user_identify):
                    self.message = "新建转库单成功"
                    self.signal = 0
                else:
                    self.message = "新建转库单失败"
                    self.signal = 1
            except:
                traceback.print_exc()
                self.message = "新建转库单失败"
                self.signal = 1
        else:
            st = models.Transfer.objects.filter(st_identify=st_identify)
            if st:
                if st.update(organization=organization, st_to_house=st_to_house, st_date=st_date):
                    pass
                else:
                    self.message = "更新失败"
                    self.signal = 1
            else:
                self.message = "更新失败"
                self.signal = 1
        return Response({"message": self.message, "signal": self.signal, "str_new_identify": self.st_new_identify})


class TransferDetailSaveView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "转库单详情保存成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        st_identify = data['st_identify']
        tds = data['tds']
        models.StDetail.objects.filter(transfer__st_identify=st_identify).delete()

        st = models.Transfer.objects.get(st_identify=st_identify)

        for td in tds:
            td_identify = td['td_identify']  # 物料编码
            material = Material.objects.get(material_identify=td_identify)
            str_identify = data['str_identify']
            td_apply_num = data['td_apply_num']
            td_real_num = data['td_real_num']
            td_present_num = data['td_present_num']
            td_remarks = data['td_remarks']

            try:
                if models.StDetail.objects.create(transfer=st, str_identify=str_identify, material=material,
                                                  td_apply_num=td_apply_num, td_real_num=td_real_num,
                                                  td_present_num=td_present_num):
                    pass
                else:
                    self.message = "转库单详情保存失败"
                    self.signal = 1
            except:
                traceback.print_exc()
                self.message = "转库单详情保存失败"
                self.signal = 1


class TransferDetailSubmitView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "转库单详情提交成功"
        self.signal = 0

    def post(self, request):
        """提交后将草稿改为已审批"""
        data = json.loads(request.body.decode("utf-8"))
        st_identify = data['st_identify']
        tds = data['tds']
        try:
            if models.Transfer.objects.filter(st_identify=st_identify).update(st_status=1):
                pass
            else:
                self.message = "转库单详情提交失败"
                self.signal = 1
        except:
            self.message = "转库单详情提交失败"
            self.signal = 1
        for td in tds:
            str_identify = td['str_identify']
            if str_identify:
                td_identify = td['td_identify']
                models.TrDetail.objects.filter(transfer_request__str_identify=str_identify, material__material_identify=td_identify).update(trd_used=1)
        return Response({'message': self.message, 'signal': self.signal})


class TransferDeleteView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "删除转库单成功"
        self.signal = 0

    def post(self, request):
        """需要数据为转库单编号"""
        data = json.loads(request.body.decode("utf-8"))
        st_identify = data['st_identify']

        try:
            if models.Transfer.objects.filter(st_identify=st_identify).delete()[0]:
                pass
            else:
                self.message = "删除转库单失败"
                self.signal = 1
        except:
            self.message = "删除转库单失败"
            self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})
