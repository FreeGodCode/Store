import json
from django.shortcuts import render
from .serializer import PurchaseReceiptSerializer, PurchaseReceiptDetailSerializer
from rest_framework.views import APIView
from base.models import UserNow, Organization, UserProfile, TotalWareHouse, Supplier, Material, Department
from . import models


class PurchaseReceiptsView(APIView):
    """"""

    def __init__(self, **kwargs):
        super(PurchaseReceiptsView, self).__init__(**kwargs)
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
            prcs = models.PurchaseReceipt.objects.filter(~Q(prc_status=0), organization__area_name=self.area_name).all()
        elif permission == '2':
            prcs = models.PurchaseReceipt.objects.filter(prc_creator_identify=user_identify,
                                                    organization__area_name=self.area_name).all()
        else:
            prcs1 = models.PurchaseReceipt.objects.filter(~Q(prc_status=0), organization__area_name=self.area_name).all()
            prcs2 = models.PurchaseReceipt.objects.filter(prc_creator_identify=user_identify,
                                                     organization__area_name=self.area_name).all()
            prcs = prcs1 | prcs2
        if prcs:
            prcs_serializer = models.PurchaseReceiptSerializer(prcs, many=True)
            return Response({"prcs": prcs_serializer.data, "signal": 0})
        else:
            return Response({"message": "未查询到信息"})


class PurchaseReceiptNewView(APIView):
    """"""

    def __init__(self, **kwargs):
        super(PurchaseReceiptNewView, self).__init__(**kwargs)
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
            prc_identify = data['prc_identify']
        except:
            return Response({"supply_names": supply_names, "org_ware_houses": org_ware_houses, "signal": 0})
        else:
            prcds = models.PurchaseReceiptDetail.objects.filter(purchase_receipt__prc_identify=prc_identify).all()
            prcds_serializer = models.PurchaseReceiptDSerializer(prcds, many=True)
            return Response(
                {"supply_names": supply_names, "org_ware_houses": org_ware_houses, "prcds": prcds_serializer.data,
                 "signal": 1})


class PurchaseReceiptUpdateView(APIView):
    """"""

    def __init__(self, **kwargs):
        super(PurchaseReceiptUpdateView, self).__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0
        self.user_now_name = ""
        self.area_name = ""
        self.prc_new_identify = ""

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
        prc_date = data['prc_date']
        prc_remarks = data['prc_remarks']

        try:
            prc_identify = data['prc_identify']
        except:
            date_str = timezone.now().strftime("%Y-%m-%d")
            date = "".join(date_str.split("-"))
            pre_identify = "BI" + date
            max_id = models.PurchaseReceipt.objects.all().aggregate(Max('prc_serial'))['prc_serial__max']
            if max_id:
                prc_serial = str(int(max_id) + 1).zfill(4)
            else:
                prc_serial = "0001"
            prc_new_identify = pre_identify + prc_serial
            self.prc_new_identify = prc_new_identify
            try:
                if models.PurchaseReceipt.objects.create(prc_identify=self.prc_new_identify, prc_serial=prc_serial,
                                                    organization=organization, totalwarehouse=in_ware_house,
                                                    supplier=supplier, prc_date=prc_date, prc_remarks=prc_remarks,
                                                    prc_status=0, prc_creator=self.user_now_name,
                                                    prc_creator_identify=user_identify):
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
            prc = models.PurchaseReceipt.objects.filter(prc_identify=prc_identify)
            if prc:
                prc.update(organization=organization, totalwarehouse=in_ware_house, supplier=supplier,
                           prc_date=prc_date, prc_remarks=prc_remarks)
            else:
                self.message = "更新失败"
                self.signal = 1
        return Response({"message": self.message, "signal": self.signal, "prc_new_identify": self.prc_new_identify})


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


class PurchaseReceiptDetailSaveView(APIView):
    def __init__(self, **kwargs):
        super(PurchaseReceiptDetailSaveView, self).__init__(**kwargs)
        self.message = "采购入库单详情保存成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        prcds = data["prcds"]
        prcd_identify = data["prcd_identify"]
        models.PurchaseReceiptDetail.objects.filter(purchase_receipt__prc_identify=prcd_identify).delete()
        prc = models.PurchaseReceipt.objects.get(prc_identify=prc_identify)
        for prcd in prcds:
            prcd_identify = prcd['prcd_identify']
            material = Material.objects.get(material_identify=prcd_identify)
            prcd_paper_num = prcd['prcd_paper_num']
            prcd_real_num = prcd['prcd_real_num']
            prcd_unitPrice = prcd['prcd_unitPrice']
            prcd_sum = prcd['prcd_sum']
            po_identify = prcd['po_identify']
            prq_identify = prcd['prq_identify']

            try:
                if models.PurchaseReceiptDetail.objects.create(purchase_receipt=prc, material=material,
                                                          prcd_paper_num=prcd_paper_num,
                                                          prcd_real_num=prcd_real_num, prcd_unitPrice=prcd_unitPrice,
                                                          prcd_sum=prcd_sum,
                                                          po_identify=po_identify, prq_identify=prq_identify):
                    pass
                else:
                    self.message = "采购入库单详情保存失败"
                    self.signal = 1
            except:
                traceback.print_exc()
                self.message = "采购入库单详情保存失败"
                self.signal = 1

        return Response({'message': self.message, 'signal': self.signal})


class PurchaseReceiptDetailSubmitView(APIView):
    def __init__(self, **kwargs):
        super(PurchaseReceiptDetailSubmitView, self).__init__(**kwargs)
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

        prc_identify = data["prc_identify"]
        prcds = data["prcds"]
        in_ware_house = data["in_ware_house"]
        org_name = data["org_name"]
        try:
            if models.PurchaseReceipt.objects.filter(prc_identify=prc_identify).update(prc_status=1):
                pass
            else:
                self.message = "采购入库单提交保存失败"
                self.signal = 1
        except:
            traceback.print_exc()
            self.message = "采购入库单提交保存失败"
            self.signal = 1
        for prcd in prcds:
            prcd_identify = data['prcd_identify']  # 物料编码
            prcd_real_num = prcd['prcd_real_num']
            prcd_unitPrice = prcd['prcd_unitPrice']

            totaL_stock = TotalStock.objects.get(
                totalwarehouse__total_name=in_ware_house,
                totalwarehouse__organization__area_name=self.area_name,
                totalwarehouse__organization__org_name=org_name,
                material__material_identify=prcd_identify
            )
            ts_present_num = totaL_stock.ts_present_num
            ts_present_price = totaL_stock.ts_present_price

            ts_new_num = ts_present_num + prcd_real_num
            ts_new_price = (prcd_real_num * prcd_unitPrice + ts_present_num * ts_present_price) / ts_new_num

            try:
                if TotalStock.objects.filter(
                        totalwarehouse__total_name=in_ware_house,
                        totalwarehouse__organization__area_name=self.area_name,
                        totalwarehouse__organization__org_name=org_name,
                        material__material_identify=prcd_identify
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


class PurchaseReceiptDeleteView(APIView):
    """"""

    def __init__(self, **kwargs):
        super(PurchaseReceiptDeleteView, self).__init__(**kwargs)
        self.message = "删除采购入库单成功"
        self.signal = 0

    def post(self, request):
        """需要数据为合同编号"""
        data = json.loads(request.body.decode("utf-8"))
        prc_identify = data['prc_identify']

        try:
            if models.PurchaseReceipt.objects.filter(prc_identify=prc_identify).delete()[0]:
                pass
            else:
                self.message = "删除采购入库单失败"
                self.signal = 1
        except:
            traceback.print_exc()
            self.message = "删除采购入库单失败"
            self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})
