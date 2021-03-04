import json
from django.shortcuts import render
from .serializer import BuyInStoreSerializer, BuyInStoreDetailSerializer
from rest_framework.views import APIView
from ..base.models import UserNow, Organization, UserProfile, TotalWareHouse, Supplier, Material, Department
from . import models


class BuyInStoresView(APIView):
    """"""

    def __init__(self, **kwargs):
        super(BuyInStoresView, self).__init__(**kwargs)
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
            biss = models.BuyInStore.objects.filter(~Q(bis_status=0), organization__area_name=self.area_name).all()
        elif permission == '2':
            biss = models.BuyInStore.objects.filter(bis_creator_identify=user_identify,
                                                    organization__area_name=self.area_name).all()
        else:
            biss1 = models.BuyInStore.objects.filter(~Q(bis_status=0), organization__area_name=self.area_name).all()
            biss2 = models.BuyInStore.objects.filter(bis_creator_identify=user_identify,
                                                     organization__area_name=self.area_name).all()
            biss = biss1 | biss2
        if biss:
            biss_serializer = models.BuyInStoreSerializer(biss, many=True)
            return Response({"biss": biss_serializer.data, "signal": 0})
        else:
            return Response({"message": "未查询到信息"})


class BuyInStoreNewView(APIView):
    """"""

    def __init__(self, **kwargs):
        super(BuyInStoreNewView, self).__init__(**kwargs)
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

        supply_names = Supplier.objects.filter(supply_status=1).values_list('id', 'supply_name')

        try:
            bis_identify = data['bis_identify']
        except:
            return Response({"supply_names": supply_names, "org_ware_houses": org_ware_houses, "signal": 0})
        else:
            bds = models.BuyInStoreDetail.objects.filter(buy_in_store__bis_identify=bis_identify).all()
            bds_serializer = models.BuyInStoreDSerializer(bds, many=True)
            return Response(
                {"supply_names": supply_names, "org_ware_houses": org_ware_houses, "bds": bds_serializer.data,
                 "signal": 1})


class BuyInStoreUpdateView(APIView):
    """"""

    def __init__(self, **kwargs):
        super(BuyInStoreUpdateView, self).__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0
        self.user_now_name = ""
        self.area_name = ""
        self.bis_new_identify = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_now_identify']
        user_now = UserNow.objects.get(user_identify=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name
        org_name = data['org_name']
        organization = Organization.objects.get(area_name=self.area_name, org_name=org_name)
        supply_name = data['supply_name']
        supplier = Supplier.objects.get(supply_name=supply_name)
        in_ware_house = data['in_ware_house']
        in_ware_house = TotalWareHouse.objects.get(organization__area_name=self.area_name, total_name=in_ware_house)
        bis_date = data['bis_date']
        bis_remarks = data['bis_remarks']

        try:
            bis_identify = data['bis_identify']
        except:
            date_str = timezone.now().strftime("%Y-%m-%d")
            date = "".join(date_str.split("-"))
            pre_identify = "BI" + date
            max_id = models.BuyInStore.objects.all().aggregate(Max('bis_serial'))['bis_serial__max']
            if max_id:
                bis_serial = str(int(max_id) + 1).zfill(4)
            else:
                bis_serial = "0001"
            bis_new_identify = pre_identify + bis_serial
            self.bis_new_identify = bis_new_identify
            try:
                if models.BuyInStore.objects.create(bis_identify=self.bis_new_identify, bis_serial=bis_serial,
                                                    organization=organization, totalwarehouse=in_ware_house,
                                                    supplier=supplier, bis_date=bis_date, bis_remarks=bis_remarks,
                                                    bis_status=0, bis_creator=self.user_now_name,
                                                    bis_creator_identify=user_identify):
                    self.message = "新建采购入库单成功"
                    self.signal = 0
                else:
                    self.message = "新建采购入库单失败"
                    self.signal = 1
            except:
                traceback.print_exc()
                self.message = "新建采购入库单失败"
                self.signal = 1
        else:
            bis = models.BuyInStore.objects.filter(bis_identify=bis_identify)
            if bis:
                bis.update(organization=organization, totalwarehouse=in_ware_house, supplier=supplier,
                           bis_date=bis_date, bis_remarks=bis_remarks)
            else:
                self.message = "更新失败"
                self.signal = 1
        return Response({"message": self.message, "signal": self.signal, "bis_new_identify": self.bis_new_identify})


class PurchaseOrderChoiceView(APIView):
    """"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_now_name = ""
        self.area_name = ""
        self.pos = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_now_identify']
        user_now = UserNow.objects.get(user_identify=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name

        try:
            org_name = data['org_name']
        except:
            return Response({"message": "不传了，气死我了"})
        else:
            print(org_name)
            print(self.area_name)
            self.pos = PurchaseOrder.objects.get(organization__area_name=self.area_name,
                                                 organization__org_name=org_name, po_status=1)
        finally:
            pos_serializer = PurchaseOrderSerializer(self.pos, many=True)
            ords_list = []
            for po in self.pos:
                po_identify = po.po_identify
                ords = OrderDetail.objects.filter(purchase_order__po_identify=po_identify).all()
                ords_serializer = OrderDetailSerializer(ords, many=True)
                ords_list.append(ords_serializer.data)
            return Response({"pos": pos_serializer.data, "ords": ords_list, "signal": 0})  # 订单和对应的订单明细


class BuyInStoreDetailSaveView(APIView):
    def __init__(self, **kwargs):
        super(BuyInStoreDetailSaveView, self).__init__(**kwargs)
        self.message = "采购入库单详情保存成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        bds = data["bds"]
        bis_identify = data["bis_identify"]
        models.BuyInStoreDetail.objects.filter(buy_in_store__bis_identify=bis_identify).delete()
        bis = models.BuyInStore.objects.get(bis_identify=bis_identify)
        for bd in bds:
            bd_identify = bd['bd_identify']
            material = Material.objects.get(material_identify=bd_identify)
            bd_paper_num = bd['bd_paper_num']
            bd_real_num = bd['bd_real_num']
            bd_unitPrice = bd['bd_unitPrice']
            bd_sum = bd['bd_sum']
            po_identify = bd['po_identify']
            pr_identify = bd['pr_identify']

            try:
                if models.BuyInStoreDetail.objects.create(buy_in_store=bis, material=material,
                                                          bd_paper_num=bd_paper_num,
                                                          bd_real_num=bd_real_num, bd_unitPrice=bd_unitPrice,
                                                          bd_sum=bd_sum,
                                                          po_identify=po_identify, pr_identify=pr_identify):
                    pass
                else:
                    self.message = "采购入库单详情保存失败"
                    self.signal = 1
            except:
                traceback.print_exc()
                self.message = "采购入库单详情保存失败"
                self.signal = 1

        return Response({'message': self.message, 'signal': self.signal})


class BuyInStoreDetailSubmitView(APIView):
    def __init__(self, **kwargs):
        super(BuyInStoreDetailSubmitView, self).__init__(**kwargs)
        self.message = "采购入库单提交保存成功"
        self.signal = 0
        self.user_now_name = ""
        self.area_name = ""

    def post(self, request):
        """提交后将草稿改为已审批，需要数据为 """
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_now_identify']
        user_now = UserNow.objects.get(user_identify=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name

        bis_identify = data["bis_identify"]
        bds = data["bds"]
        in_ware_house = data["in_ware_house"]
        org_name = data["org_name"]
        try:
            if models.BuyInStore.objects.filter(bis_identify=bis_identify).update(bis_status=1):
                pass
            else:
                self.message = "采购入库单提交保存失败"
                self.signal = 1
        except:
            traceback.print_exc()
            self.message = "采购入库单提交保存失败"
            self.signal = 1
        for bd in bds:
            bd_identify = data['bd_identify']  # 物料编码
            bd_real_num = bd['bd_real_num']
            bd_unitPrice = bd['bd_unitPrice']

            totaL_stock = TotalStock.objects.get(
                totalwarehouse__total_name=in_ware_house,
                totalwarehouse__organization__area_name=self.area_name,
                totalwarehouse__organization__org_name=org_name,
                material__material_identify=bd_identify
            )
            ts_present_num = totaL_stock.ts_present_num
            ts_present_price = totaL_stock.ts_present_price

            ts_new_num = ts_present_num + bd_real_num
            ts_new_price = (bd_real_num * bd_unitPrice + ts_present_num * ts_present_price) / ts_new_num

            try:
                if TotalStock.objects.filter(
                        totalwarehouse__total_name=in_ware_house,
                        totalwarehouse__organization__area_name=self.area_name,
                        totalwarehouse__organization__org_name=org_name,
                        material__material_identify=bd_identify
                ).update(ts_present_num=ts_new_num, ts_present_price=ts_new_price):
                    pass
                else:
                    self.message = "仓库价格更新错误"
                    self.signal = 1
            except:
                traceback.print_exc()
                self.message = "仓库价格更新错误"
                self.signal = 1

        return Response({'message': self.message, 'signal': self.signal})


class BuyInStoreDeleteView(APIView):
    """"""

    def __init__(self, **kwargs):
        super(BuyInStoreDeleteView, self).__init__(**kwargs)
        self.message = "删除采购入库单成功"
        self.signal = 0

    def post(self, request):
        """需要数据为合同编号"""
        data = json.loads(request.body.decode("utf-8"))
        bis_identify = data['bis_identify']

        try:
            if models.BuyInStore.objects.filter(bis_identify=bis_identify).delete()[0]:
                pass
            else:
                self.message = "删除采购入库单失败"
                self.signal = 1
        except:
            traceback.print_exc()
            self.message = "删除采购入库单失败"
            self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})
