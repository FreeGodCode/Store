import json

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Q, Max
# from django.shortcuts import render, redirect
from storeManage.models import TotalStock
from storeManage.serializer import TotalStockSerializer
from . import models
from ..base.models import UserNow, Organization, Customer, Material, TotalWareHouse
# from . models import SellOrder, SellOrderDetail
from .serializer import SellOrderSerializer, SellOrderDetailSerializer


class SellOrdersView(APIView):
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

        power = data['power']
        sos = ""
        if power == '1':
            sos = models.SellOrder.objects.filter(~Q(so_status=0), organization__area_name=self.area_name).all()

        if power == '2':
            sos = models.SellOrder.objects.filter(so_creator_iden=user_identify,
                                                  organization__area_name=self.area_name).all()
        elif power == '3':
            sos1 = models.SellOrder.objects.filter(~Q(so_status=0), organization__area_name=self.area_name).all()
            sos2 = models.SellOrder.objects.filter(so_creator_iden=user_identify,
                                                   organization__area_name=self.area_name).all()
            sos = sos1 | sos2
        if sos:
            sos_serializer = SellOrderSerializer(sos, many=True)
            return Response({"sos": sos_serializer.data, "signal": 0})
        else:
            return Response({"message": "未查询到数据"})


class SellOrderNewView(APIView):
    """
    新建和编辑的时候都可以post这个
    返回的数据为组织名字和id、客户名字和id、发货仓库的组织名字，仓库名字和id
    """

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
            deliver_ware_houses = TotalWareHouse.objects.filter(organization=organization, total_status=1).values_list(
                "total_name", flat=True)
            org_ware_houses[org_name] = deliver_ware_houses

        customers = Customer.objects.filter(customer_status=1).values_list("id", "customer_name")

        try:
            so_identify = data['so_identify']
            org_name = data['org_name']
            deliver_ware_house = data['deliver_ware_house']
        except:
            return Response(
                {"org_ware_houses": org_ware_houses, "customers": customers, "signal": 0})
        else:
            sods = models.SellOrderDetail.objects.filter(sell_order__so_identify=so_identify)
            print("SSs")
            sods_serializers = SellOrderDetailSerializer(sods, many=True)
            sods_present_num = []
            for sod in sods:
                material = sod.material
                try:
                    sod_present_num = TotalStock.objects.get(totalwarehouse__organization__org_name=org_name,
                                                             totalwarehouse__organization__area_name=self.area_name,
                                                             totalwarehouse__total_name=deliver_ware_house,
                                                             material=material).ts_present_num
                except:
                    sod_present_num = 0
                sods_present_num.append(sod_present_num)

            return Response({"org_ware_houses": org_ware_houses, "customers": customers,
                             "sods": sods_serializers.data, "sods_present_num": sods_present_num, "signal": 1})


class SellOrderUpdateView(APIView):
    """
        只读取添加的数据，订单号自动生成，用于保存新增和编辑的订单
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0
        self.user_now_name = ""
        self.area_name = ""
        self.so_new_identify = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_now_identify']
        user_now = UserNow.objects.get(user_identify=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name
        org_name = data['org_name']
        organization = Organization.objects.get(org_name=org_name, area_name=self.area_name)
        customer_name = data['customer_name']
        customer = Customer.objects.get(customer_name=customer_name)
        deliver_ware_house = data['deliver_ware_house']
        so_type = data['so_type']
        so_date = data['so_date']
        so_remarks = data['so_remarks']

        try:
            so_identify = data['so_identify']
        except:
            date_str = timezone.now().strftime("%Y-%m-%d")
            date = "".join(date_str.split("-"))
            pre_identify = "SO" + date
            max_id = models.SellOrder.objects.all().aggregate(Max('so_serial'))['so_serial__max']
            if max_id:
                so_serial = str(int(max_id) + 1).zfill(4)
            else:
                so_serial = "0001"
            so_new_identify = pre_identify + so_serial
            self.so_new_identify = so_new_identify
            try:
                if models.SellOrder.objects.create(so_identify=so_new_identify, so_serial=so_serial,
                                                   organization=organization,
                                                   so_type=so_type, customer=customer, so_date=so_date,
                                                   deliver_ware_house=deliver_ware_house,
                                                   so_remarks=so_remarks,
                                                   so_status=0, so_creator=self.user_now_name,
                                                   so_creator_iden=user_identify):
                    self.message = "新建销售订单成功"
                    self.signal = 0
                else:
                    self.message = "新建销售订单失败"
                    self.signal = 1
            except:

                self.message = "新建销售订单失败"
                self.signal = 1
        else:
            so = models.SellOrder.objects.filter(so_identify=so_identify)
            if so:
                if so.update(organization=organization, so_type=so_type, customer=customer, so_date=so_date,
                             deliver_ware_house=deliver_ware_house, so_remarks=so_remarks):
                    pass
                else:
                    self.message = "更新失败"
                    self.signal = 1

            else:
                self.message = "更新失败"
                self.signal = 1
        return Response({"message": self.message, "signal": self.signal, "so_new_identify": self.so_new_identify})


class SellOrderDetailSaveView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "销售订单详情保存成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        so_identify = data['so_identify']
        sods = data['sods']
        models.SellOrderDetail.objects.filter(sell_order__so_identify=so_identify).delete()

        so = models.SellOrder.objects.get(so_identify=so_identify)
        for sod in sods:
            # id = sod['id']
            sod_identify = sod['sod_identify']  # 物料编码
            material = Material.objects.get(material_iden=sod_identify)
            sod_num = sod['sod_num']  # 销售数量
            sod_taxRate = sod['sod_taxRate']
            sod_tax_unitPrice = sod['sod_tax_unitPrice']
            sod_unitPrice = sod['sod_unitPrice']
            sod_tax_sum = sod['sod_tax_sum']
            sod_sum = sod['sod_sum']
            sod_tax_price = sod['sod_tax_price']
            sod_remarks = sod['sod_remarks']

            try:
                if models.SellOrderDetail.objects.create(sell_order=so, material=material,
                                                         sod_num=sod_num,
                                                         sod_taxRate=sod_taxRate,
                                                         sod_tax_unitPrice=sod_tax_unitPrice,
                                                         sod_unitPrice=sod_unitPrice,
                                                         sod_tax_sum=sod_tax_sum,
                                                         sod_sum=sod_sum,
                                                         sod_tax_price=sod_tax_price,
                                                         sod_remarks=sod_remarks):
                    pass
                else:
                    self.message = "销售订单详情保存失败"
                    self.signal = 1
            except:
                self.message = "销售订单详情保存失败"
                self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})


class SellOrderDetailSubmitView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "销售订单详情提交成功"
        self.signal = 0

    def post(self, request):
        """提交后将草稿改为已审批，需要数据为"""
        data = json.loads(request.body.decode("utf-8"))
        so_identify = data['so_identify']

        try:
            if models.SellOrder.objects.filter(so_identify=so_identify).update(so_status=1):
                pass
            else:
                self.message = "销售订单提交保存失败"
                self.signal = 1
        except:
            self.message = "销售订单提交保存失败"
            self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})


class SellOrderDetailNewView(APIView):
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
        deliver_ware_house = data['deliver_ware_house']

        total_ware_house = TotalWareHouse.objects.filter(organization__org_name=org_name,
                                                         organization__area_name=self.area_name,
                                                         total_name=deliver_ware_house).first()
        print(total_ware_house)
        total_stocks = total_ware_house.total_ware_house_ts.all()
        if total_stocks:

            total_stocks_serializer = TotalStockSerializer(total_stocks, many=True)
            return Response({"materials": total_stocks_serializer.data})
        else:
            return Response({"message": "仓库空空如也"})


# class SellOrderDetailNewSaveView(APIView):
#
#     def post(self, request):
#         data = json.loads(request.body.decode("utf-8"))
#         so_identify = data['so_identify']
#         sods = data['sods']
#         for sod in sods:
#             sod_identify = sod['sod_identify']  # 物料编码
#             material = Material.objects.get(material_iden=sod_identify)
#             so = models.SellOrder.objects.get(so_identify=so_identify)
#             try:
#                 if models.SellOrderDetail.objects.create(sell_order=so, material=material, sod_num=0):
#                     pass
#                 else:
#                     return Response({"message": "新建物料错误"})
#             except:
#                 return Response({"message": "新建物料错误"})
#
#         return Response({"message": "新建物料详情成功", "signal": 0})

#
# class SellOrderDetailDeleteView(APIView):
#     def post(self, request):
#         """
#         需要获取物料编号就可以了
#         """
#         data = json.loads(request.body.decode("utf-8"))
#
#         sods = data['sods']
#         for sod in sods:
#             sod_identify = sod['sod_identify']
#             try:
#                 if models.SellOrderDetail.objects.filter(sod_identify=sod_identify).delete()[0]:
#                     pass
#                 else:
#                     return Response({"message": "删除物料错误"})
#             except:
#                 return Response({"message": "删除物料错误"})
#
#         return Response({"message": "删除物料成功"})


class SellOrderDeleteView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "删除销售订单成功"
        self.signal = 0

    def post(self, request):

        data = json.loads(request.body.decode("utf-8"))
        so_identify = data['so_identify']

        try:
            if models.SellOrder.objects.filter(so_identify=so_identify).delete()[0]:
                pass
            else:
                self.message = "删除销售订单失败"
                self.signal = 1
        except:
            self.message = "删除销售订单失败"
            self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})

# class SellOrderCloseView(APIView):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.message = "关闭销售订单成功"
#         self.signal = 0
#
#     def post(self, request):
#         """
#         需要数据为请购单编号、关闭人、关闭原因
#         """
#         data = json.loads(request.body.decode("utf-8"))
#         so_identify = data['so_identify']
#         so_closer = data['so_closer']
#         so_closerReason = data['so_closerReason']
#
#         try:
#             models.PurchaseRequest.objects.filter(so_identify=so_identify).update(so_status=2, so_closer=so_closer,
#                                                                           so_closerReason=so_closerReason)
#
#         except:
#             self.message = "关闭请购单失败"
#             self.signal = 1
#         return Response({'message': self.message, 'signal': self.signal})
