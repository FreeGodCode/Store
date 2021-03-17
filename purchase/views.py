import json
import datetime
import traceback
from rest_framework.views import APIView
from rest_framework. response import Response

from django.shortcuts import render
from django.db.models import Q, Max
from django.utils import timezone
from base.models import UserNow, Supplier, Department, Organization, Material
from purchaseRequest.models import PurchaseRequest
from . import models, serializer

from .models import PurchaseContractDetail
from .serializer import PurchaseContractDetailSerializer, PurchaseOrderSerializer, OrderDetailSerializer, \
    PurchaseContractSerializer


class PurchaseContractsView(APIView):
    def __init__(self, **kwargs):
        super(PurchaseContractsView, self).__init__(**kwargs)
        self.user_now_name = ""
        self.area_name = ""

    def post(self, request):
        """需要获取区域名字，用户编号 """
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_now_identify']
        user_now = UserNow.objects.get(user_identify=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name

        permission = data['permission']
        print(permission)
        if permission == '1':
            pcs = models.PurchaseContract.objects.filter(~Q(pc_status=0), organization__area_name=self.area_name).all()
        elif permission == '2':
            pcs = models.PurchaseContract.objects.filter(pc_creator_iden=user_identify, organization__area_name=self.area_name).all()
        else:
            pcs1 = models.PurchaseContract.objects.filter(~Q(pc_status=0), organization__area_name=self.area_name).all()
            pcs2 = models.PurchaseContract.objects.filter(pc_creator_iden=user_identify, organization__area_name=self.area_name).all()
            pcs = pcs1 | pcs2
        if pcs:
            pcs_serializer = serializer.PurchaseContractSerializer(pcs, many=True)
            return Response({"pcs": pcs_serializer.data, "signal": 0})
        else:
            return Response({"message": "未查询到信息"})


class PurchaseContractNewView(APIView):
    """"""
    def __init__(self, **kwargs):
        super(PurchaseContractNewView, self).__init__(**kwargs)
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
        supply_names = Supplier.objects.filter(supply_status=1).values_list('id', 'supply_name')
        try:
            pc_identify = data['pc_identify']
            org_name = data['org_name']
        except:
            return Response({"org_names": org_names, "supply_names": supply_names, "signal": 0})
        else:
            pcds = models.PurchaseContractDetail.objects.filter(purchase_contract__pc_identify=pc_identify)
            pcds_serializer = serializer.PurchaseContractDetailSerializer(pcds, many=True)
            pays = models.PurchaseContractPayDetail.objects.filter(purchase_contract__pc_identify=pc_identify)
            pays_serializer = serializer.PurchaseContractPaySerializer(pays, many=True)
            return Response({
                "org_names": org_names, "supply_names": supply_names, "pcds": pcds_serializer.data,
                "pays": pays_serializer.data, "signal": 1
            })


class PurchaseContractUpdateView(APIView):
    """订单合同更新"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0
        self.user_now_name = ""
        self.area_name = ""
        self.pc_new_identify = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_identify']
        user_now = UserNow.objects.get(user_iden=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name

        org_name = data['org_name']
        organization = Organization.objects.get(area_name=self.area_name, org_name=org_name)
        supply_name = data['supply_name']
        supplier = Supplier.objects.get(supply_name=supply_name)
        pc_name = data['pc_name']
        pc_date = data['pc_date']
        pc_sum = data['pc_sum']
        pc_remarks = data['pc_remarks']

        try:
            pc_identify = data['pc_identify']
        except:
            date_str = timezone.now().strftime("%Y-%m-%d")
            date = "".join(date_str.split("-"))
            pre_identify = "PC" + date
            max_id = models.PurchaseContract.objects.all().aggregate(Max('pc_serial'))['pc_serial__max']
            if max_id:
                pc_serial = str(int(max_id) + 1).zfill(4)
            else:
                pc_serial = "0001"
            pc_new_identify = pre_identify + pc_serial
            self.pc_new_identify = pc_new_identify
            try:
                if models.PurchaseContract.objects.create(pc_identify=self.pc_new_identify, pc_serial=pc_serial,
                                                          organization=organization, pc_name=pc_name, supplier=supplier,
                                                          pc_date=pc_date, pc_sum=pc_sum, pc_remarks=pc_remarks,
                                                          pc_status=0, pc_creator=self.user_now_name,
                                                          pc_creator_iden=user_identify):

                    self.message = "新建采购合同成功"
                    self.signal = 0
                else:
                    self.message = "新建采购合同失败"
                    self.signal = 1
            except:
                traceback.print_exc()
                self.message = "新建采购合同失败"
                self.signal = 1
        else:
            pc = models.PurchaseContract.objects.filter(pc_identify=pc_identify)
            if pc:
                pc.update(organization=organization, pc_name=pc_name, supplier=supplier, pc_date=pc_date,
                          pc_sum=pc_sum, pc_remarks=pc_remarks)
            else:
                self.message = "更新失败"
                self.signal = 1
        return Response({"message": self.message, "signal": self.signal, "pc_new_identify": self.pc_new_identify})


class PurchaseContractDetailSaveView(APIView):
    def __init__(self, **kwargs):
        super(PurchaseContractDetailSaveView).__init__(**kwargs)
        self.message = "合同详情保存成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        pcds = data['pcds']
        pc_identify = data['pc_identify']
        pays = data['pays']
        models.CdDetail.objects.filter(purchase_contract__pc_identify=pc_identify).delete()
        pc = models.PurchaseContract.objects.get(pc_identify=pc_identify)
        pc_sum = data['pc_sum']
        models.PurchaseContract.objects.filter(pc_identify=pc_identify).update(pc_sum=pc_sum)
        for pcd in pcds:
            pcd_identify = pcd['pcd_identify']
            material = Material.objects.get(material_iden=pcd_identify)
            pcd_num = pcd['pcd_num']  # 销售数量
            pcd_taxRate = pcd['pcd_taxRate']
            pcd_tax_unitPrice = pcd['pcd_tax_unitPrice']
            pcd_unitPrice = pcd['pcd_unitPrice']
            pcd_tax_sum = pcd['pcd_tax_sum']
            pcd_sum = pcd['pcd_sum']
            pcd_tax_price = pcd['pcd_tax_price']
            pcd_pr_identify = pcd['pcd_pr_identify']
            pcd_prd_remarks = pcd['pcd_prd_remarks']
            # PurchaseContractDetail.objects.filter(purchase_request__pr_identify=pc_identify, prd_iden=pcd_identify).update(prd_uesd=1)
            # 更新请购单物料使用状态
            try:
                if models.CdDetail.objects.create(purchase_contract=pc, material=material,
                                                  pcd_num=pcd_num, pcd_taxRate=pcd_taxRate,
                                                  pcd_tax_unitPrice=pcd_tax_unitPrice,
                                                  pcd_unitPrice=pcd_unitPrice,
                                                  pcd_tax_sum=pcd_tax_sum, pcd_sum=pcd_sum,
                                                  pcd_tax_price=pcd_tax_price,
                                                  pcd_pr_identify=pcd_pr_identify,
                                                  pcd_prd_remarks=pcd_prd_remarks):
                    pass
                else:
                    self.message = "合同详情保存失败"
                    self.signal = 1

            except:
                traceback.print_exc()
                self.message = "合同详情保存失败"
                self.signal = 1
        models.CdPayDetail.objects.filter(purchase_contract__pc_identify=pc_identify).delete()
        for pay in pays:
            pay_batch = pay['pay_batch']
            pay_rate = pay['pay_rate']
            pay_price = pay['pay_price']
            pay_planDate = pay['pay_planDate']
            pay_prepay = pay['pay_prepay']
            pay_remarks = pay['pay_remarks']
            try:
                if models.CdPayDetail.objects.create(purchase_contract=pc, pay_batch=pay_batch, pay_rate=pay_rate,
                                                     pay_price=pay_price, pay_planDate=pay_planDate,
                                                     pay_prepay=pay_prepay,
                                                     pay_remarks=pay_remarks):
                    pass
                else:
                    self.message = "合同详情保存失败"
                    self.signal = 1
            except:
                self.message = "合同详情保存失败"
                self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})


class PurchaseContractDetailSubmitView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_now_name = ""
        self.area_name = ""
        self.message = "合同明细提交成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_identify']
        user_now = UserNow.objects.get(user_iden=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name
        pc_identify = data['pc_identify']
        pcds = data['pcds']
        try:
            if models.PurchaseContract.objects.filter(pc_identify=pc_identify).update(pc_status=1):
                pass
            else:
                self.message = "合同明细提交失败"
                self.signal = 1
        except:
            self.message = "合同明细提交失败"
            self.signal = 1

        for pcd in pcds:
            pcd_identify = pcd['pcd_identify']
            pcd_pr_identify = pcd['pcd_pr_identify']
            PurchaseContractDetail.objects.filter(purchase_request__pr_identify=pcd_pr_identify, material__material_iden=pcd_identify).update(
                prd_used=1)
            prds = PurchaseContractDetail.objects.filter(purchase_request__pr_identify=pcd_pr_identify).all()
            pr = PurchaseRequest.objects.filter(pr_identify=pcd_pr_identify)
            flag = 0
            for prd in prds:
                if prd.prd_used == 0:
                    flag = 1
            if flag == 0:
                pr.update(pr_status=2, pr_closer=self.user_now_name, pr_closer_identify=user_identify,
                          pr_closeDate=datetime.now(), pr_closeReason="自动关闭")
            # 更新请购单物料使用状态

        return Response({'message': self.message, 'signal': self.signal})


class PurchaseContractDetailNewView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_now_name = ""
        self.area_name = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_identify']
        user_now = UserNow.objects.get(user_iden=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name

        try:
            org_name = data['org_name']
        except:
            prds = PurchaseContractDetail.objects.filter(purchase_request__organization__area_name=self.area_name,
                                           purchase_request__pr_status=1,
                                           prd_used=0).all()
            prds_serializer = PurchaseContractDetailSerializer(prds, many=True)
            return Response({"prds": prds_serializer.data, 'signal': 0})
        else:
            prds = PurchaseContractDetail.objects.filter(purchase_request__organization__org_name=org_name,
                                           purchase_request__organization__area_name=self.area_name,
                                           purchase_request__pr_status=1,
                                           prd_used=0).all()
            prds_serializer = PurchaseContractDetailSerializer(prds, many=True)
            return Response({"prds": prds_serializer.data, 'signal': 0})


# class CdDetailNewSaveView(APIView):
#
#     def post(self):
#         data = json.loads(request.body.decode("utf-8"))
#         pc_identify = data['pc_identify']
#         pc = models.PurchaseContract.objects.get(pc_identify=pc_identify)
#         pr_identify = data['pr_identify']
#         prds = data['prds']
#         for prd in prds:
#             prd_iden = prd['prd_iden']
#             prd_num = prd['prd_num']
#             material = Material.objects.get(material_iden=prd_iden)
#             # pr = PurchaseRequest.objects.get(pr_identify=pr_identify)
#             # 这里面请购单的userd状态还没有改，后面要判断
#             try:
#                 models.CdDetail.objects.create(purchase_contract=pc, material=material,
#                                                pcd_num=prd_num, pcd_pr_identify=pr_identify)
#             except:
#                 return Response({"message": "新建合同物料详情出现错误"})
#         return Response({"message": "新建合同物料详情成功", "signal": 0})


# class CdDetailDeleteView(APIView):
#
#     def post(self, request):
#         data = json.loads(request.body.decode("utf-8"))
#         pcds = data['pcds']
#         for pcd in pcds:
#             # pcd_rp_identify = pcd['pcd_rp_identify'] # 请购单号
#             pcd_identify = pcd['pcd_identify']  # 物料编码
#             try:
#                 models.CdDetail.objects.filter(pcd_identify=pcd_identify).delete()
#             except:
#                 return Response({"message": "删除物料错误"})
#         return Response({"message": "删除物料成功", "signal": 0})


class PurchaseContractDeleteView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "删除合同成功"
        self.signal = 0

    def post(self, request):
        """
        需要数据为合同编号
        """
        data = json.loads(request.body.decode("utf-8"))
        pc_identify = data['pc_identify']

        try:
            if models.PurchaseContract.objects.filter(pc_identify=pc_identify).delete()[0]:
                pass
            else:
                self.message = "删除合同失败"
                self.signal = 1
        except:
            self.message = "删除合同失败"
            self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})


"""
采购订单
"""


class PurchaseOrdersView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_now_name = ""
        self.area_name = ""

    def post(self, request):
        """
        需要获取区域名字，用户编号
        """
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_identify']
        user_now = UserNow.objects.get(user_iden=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name

        permission = data['permission']
        print(permission)

        if permission == '1':
            pos = models.PurchaseOrder.objects.filter(~Q(po_status=0), organization__area_name=self.area_name).all()
        elif permission == '2':
            pos = models.PurchaseOrder.objects.filter(po_creator_iden=user_identify,
                                                      organization__area_name=self.area_name).all()
        else:
            pos1 = models.PurchaseOrder.objects.filter(~Q(po_status=0), organization__area_name=self.area_name).all()
            pos2 = models.PurchaseOrder.objects.filter(po_creator_iden=user_identify,
                                                       organization__area_name=self.area_name).all()
            pos = pos1 | pos2
        if pos:
            pos_serializer = PurchaseOrderSerializer(pos, many=True)
            return Response({"pos": pos_serializer.data, "signal": 0})
        else:
            return Response({"message": "未查询到信息"})


class PurchaseOrderNewView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_now_name = ""
        self.area_name = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_identify']
        user_now = UserNow.objects.get(user_iden=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name
        org_names = Organization.objects.filter(area_name=self.area_name, org_status=1).values_list('id', 'org_name')
        supply_names = Supplier.objects.filter(supply_status=1).values_list('id', 'supply_name')
        try:
            po_identify = data['po_identify']
        except:

            return Response({"org_names": org_names, "supply_names": supply_names, "signal": 0})
        else:
            ods = models.OrderDetail.objects.filter(purchase_order__po_identify=po_identify).all()
            ods_serializer = OrderDetailSerializer(ods, many=True)
            return Response({"supply_names": supply_names, "ods": ods_serializer.data, "signal": 1})


class PurchaseContractChoiceView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_now_name = ""
        self.area_name = ""
        self.prds_serializer = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_identify']
        user_now = UserNow.objects.get(user_iden=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name

        try:
            org_name = data['org_name']
        except:
            prds = PurchaseContractDetail.objects.filter(purchase_request__organization__area_name=self.area_name,
                                           purchase_request__pr_status=1,
                                           prd_used=0).all()
            self.prds_serializer = PurchaseContractDetailSerializer(prds, many=True)
        else:
            prds = PurchaseContractDetail.objects.filter(purchase_request__organization__org_name=org_name,
                                           purchase_request__organization__area_name=self.area_name,
                                           purchase_request__pr_status=1,
                                           prd_used=0).all()
            self.prds_serializer = PurchaseContractDetailSerializer(prds, many=True)
        finally:
            return Response({"prds": self.prds_serializer.data, 'signal': 0})


# class PONewByPcView(APIView):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.user_now_name = ""
#         self.area_name = ""
#         self.pcs = ""
#
#     def post(self, request):
#         data = json.loads(request.body.decode("utf-8"))
#         user_identify = data['user_now_identify']
#         user_now = UserNow.objects.get(user_identify=user_identify)
#         if user_now:
#             self.user_now_name = user_now.user_name
#             self.area_name = user_now.area_name
#         org_names =
#         try:
#             po_identify = data['po_identify']
#         except:
#              self.pcs = models.PurchaseContract.objects.filter(organization__area_name=self.area_name, pc_status=1).all()
#             pcs_serializer = PCSerializer(self.pcs, many=True)
#             pcds_list = []
#             for pc in self.pcs:
#                 pc_identify = pc.pc_identify
#                 pcds = models.CdDetail.objects.filter(purchase_contract__pc_identify=pc_identify).all()
#                 pcds_serializer = CdDSerializer(pcds, many=True)
#                 pcds_list.append(pcds_serializer.data)
#             return Response({"pcs": pcs_serializer.data, "pcds": pcds_list, "signal": 0})  # 合同和对应的合同明细
#             return Response({})
#         else:
#             ods = models.OrderDetail.objects.filter(purchase_order__po_identify=po_identify).all()
#             ods_serializer = OrDSerializer(ods, many=True)
#             return Response({"ods": ods_serializer.data, "signal": 1})


class PurchaseContractChoiceView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_now_name = ""
        self.area_name = ""
        self.pcs = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_now_identify']
        user_now = UserNow.objects.get(user_iden=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name
        try:
            org_name = data['org_name']
        except:
            self.pcs = models.PurchaseContract.objects.filter(organization__area_name=self.area_name, pc_status=1).all()
        else:
            self.pcs = models.PurchaseContract.objects.filter(organization__area_name=self.area_name, organization__org_name=org_name, pc_status=1).all()
        finally:
            pcs_serializer = PurchaseContractSerializer(self.pcs, many=True)
            pcds_list = ""
            for pc in self.pcs:
                pc_identify = pc.pc_identify
                pcds = models.CdDetail.objects.filter(purchase_contract__pc_identify=pc_identify).all()
                if pcds_list == "":
                    pcds_list = pcds
                else:
                    pcds_list = pcds_list | pcds
            pcds_serializer = PurchaseContractDetailSerializer(pcds_list, many=True)
            return Response({"pcs": pcs_serializer.data, "pcds": pcds_serializer.data, "signal": 0})  # 合同和对应的合同明细


class PurchaseOrderUpdateView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "更新成功"
        self.signal = 0
        self.user_now_name = ""
        self.area_name = ""
        self.po_new_identify = ""

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_now_identify']
        user_now = UserNow.objects.get(user_iden=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name

        org_name = data['org_name']
        organization = Organization.objects.get(area_name=self.area_name, org_name=org_name)
        supply_name = data['supply_name']
        supplier = Supplier.objects.get(supply_name=supply_name)
        po_date = data['po_date']
        po_sum = data['po_sum']
        po_remarks = data['po_remarks']
        pc_identify = data['pc_identify']

        try:
            po_identify = data['po_identify']
        except:
            date_str = timezone.now().strftime("%Y-%m-%d")
            date = "".join(date_str.split("-"))
            pre_identify = "PO" + date
            max_id = models.PurchaseOrder.objects.all().aggregate(Max('po_serial'))['po_serial__max']
            if max_id:
                po_serial = str(int(max_id) + 1).zfill(4)
            else:
                po_serial = "0001"
            po_new_identify = pre_identify + po_serial
            self.po_new_identify = po_new_identify
            try:
                if models.PurchaseOrder.objects.create(po_identify=po_new_identify, pc_identify=pc_identify, po_serial=po_serial,
                                                       organization=organization, supplier=supplier,
                                                       po_date=po_date, po_sum=po_sum, po_remarks=po_remarks,
                                                       po_status=0, po_creator=self.user_now_name,
                                                       po_creator_iden=user_identify):
                    self.message = "新建采购订单成功"
                    self.signal = 0
                else:
                    self.message = "新建采购订单失败"
                    self.signal = 1
            except:
                traceback.print_exc()
                self.message = "新建采购订单失败"
                self.signal = 1
        else:
            po = models.PurchaseOrder.objects.filter(po_identify=po_identify)
            if po:
                po.update(organization=organization, supplier=supplier, po_date=po_date, po_sum=po_sum, po_remarks=po_remarks)
            else:
                self.message = "更新失败"
                self.signal = 1
        return Response({"message": self.message, "signal": self.signal, "po_new_identify": self.po_new_identify})


class PurchaseOrderSaveView(APIView):
    """为了实现接口通用，通过发送来源合同字段"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = "采购订单详情保存成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        ods = data['ods']
        po_identify = data['po_identify']
        models.OrderDetail.objects.filter(purchase_order__po_identify=po_identify).delete()
        po = models.PurchaseOrder.objects.get(po_identify=po_identify)
        for od in ods:
            od_identify = od['od_identify']  # 物料编号
            od_num = od['od_num']  # 销售数量
            od_taxRate = od['od_taxRate']
            od_tax_unitPrice = od['od_tax_unitPrice']
            od_unitPrice = od['od_unitPrice']
            od_tax_sum = od['od_tax_sum']
            od_sum = od['od_sum']
            od_tax_price = od['od_tax_price']
            od_pr_identify = od['od_pr_identify']
            od_prd_remarks = od['od_prd_remarks']
            material = Material.objects.get(material_iden=od_identify)
            try:
                if models.OrderDetail.objects.create(purchase_order=po, material=material, od_num=od_num,
                                                  od_taxRate=od_taxRate, od_tax_unitPrice=od_tax_unitPrice,
                                                  od_tax_sum=od_tax_sum, od_sum=od_sum, od_unitPrice=od_unitPrice,
                                                  od_tax_price=od_tax_price, od_pr_identify=od_pr_identify,
                                                  od_prd_remarks=od_prd_remarks):
                    pass
                else:
                    self.message = "采购订单详情保存失败"
                    self.signal = 1
            except:
                traceback.print_exc()
                self.message = "采购订单详情保存失败"
                self.signal = 1
        return Response({'message': self.message, 'signal': self.signal})


class PurchaseOrderSubmitView(APIView):
    """为了实现接口通用，通过发送来源合同字段"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_now_name = ""
        self.area_name = ""
        self.message = "请购单提交成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_identify = data['user_identify']
        user_now = UserNow.objects.get(user_iden=user_identify)
        if user_now:
            self.user_now_name = user_now.user_name
            self.area_name = user_now.area_name
        po_identify = data['po_identify']
        ods = data['ods']
        pc_identify = data['pc_identify']  # 标识是来自合同还是请购单

        try:
            if models.PurchaseOrder.objects.filter(po_identify=po_identify).update(po_status=1):
                pass
            else:
                self.message = "请购单提交失败"
                self.signal = 1
        except:
            self.message = "请购单提交失败"
            self.signal = 1

        if pc_identify:
            pass
        else:
            for od in ods:
                od_identify = od['od_identify']
                od_pr_identify = od['od_pr_identify']
                PurchaseContractDetail.objects.filter(purchase_request__pr_identify=od_pr_identify, material__material_identify=od_identify).update(prd_used=1)
                prds = PurchaseContractDetail.objects.filter(purchase_request__pr_identify=od_pr_identify).all()
                pr = PurchaseRequest.objects.filter(pr_identify=od_pr_identify)
                flag = 0
                for prd in prds:
                    if prd.prd_used == 0:
                        flag = 1
                if flag == 0:
                    pr.update(pr_status=2, pr_closer=self.user_now_name, pr_closer_identify=user_identify, pr_closeDate=datetime.datetime.now(), pr_closeReason="自动关闭")
        return Response({'message': self.message, 'signal': self.signal})


class PurchaseOrderDeleteView(APIView):
    def __init__(self, **kwargs):
        super(PurchaseOrderDeleteView, self).__init__(**kwargs)
        self.message = "删除采购订单成功"
        self.signal = 0

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        po_identify = data['po_identify']
        try:
            if models.PurchaseOrder.objects.filter(po_identify=po_identify).delete()[0]:
                pass
            else:
                self.message = "删除采购订单失败"
                self.signal = 1
        except:
            self.message = "删除采购订单失败"
            self.signal = 1

        return Response({'message': self.message, 'signal': self.signal})