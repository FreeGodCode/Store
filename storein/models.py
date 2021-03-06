import datetime
from django.db import models


class PurchaseReceipt(models.Model):
    """采购入库单"""
    PRC_STATUS_CHOICES = (
        (0, '草稿'),
        (1, '已审批')
    )
    id = models.AutoField(primary_key=True)
    prc_identify = models.CharField(max_length=15, verbose_name='入库单编号')
    prc_serial = models.CharField(max_length=4, verbose_name='入库单流水号')
    organization = models.ForeignKey('base.Organization', verbose_name='组织', related_name='org_prc', on_delete=models.CASCADE)
    totalwarehouse = models.ForeignKey('base.TotalWareHouse', verbose_name='仓库', related_name='total_wh_prc', on_delete=models.CASCADE)
    supplier = models.ForeignKey('base.Supplier', verbose_name='供应商', related_name='supplier_prc', on_delete=models.CASCADE)
    prc_date = models.DateTimeField(default=datetime.datetime.now, verbose_name='采购入库日期')
    prc_remarks = models.TextField(max_length=400, verbose_name='采购入库单备注')
    prc_status = models.IntegerField(choices=PRC_STATUS_CHOICES, default=0, verbose_name='采购入库单状态')
    prc_creator = models.CharField(max_length=20, verbose_name='采购入库单创建人名字')
    prc_creator_identify = models.CharField(max_length=20, verbose_name='采购入库单创建人工号')
    prc_created_at = models.DateTimeField(auto_now_add=True, verbose_name='采购入库单创建日期')

    class Meta:
        db_table = 'db_purchase_receipt'
        verbose_name = "材料出库单"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.prc_identify


class PurchaseReceiptDetail(models.Model):
    """采购入库单明细"""
    id = models.AutoField(primary_key=True)
    purchase_receipt = models.ForeignKey('PurchaseReceipt', verbose_name='采购入库单', related_name='prc_prcd', on_delete=models.CASCADE)
    material = models.ForeignKey('base.Material', verbose_name='物料', related_name='material_prcd', on_delete=models.CASCADE)
    prcd_paper_num = models.IntegerField(verbose_name='应入库数量')
    prcd_real_num = models.IntegerField(verbose_name='实际入库数量')
    prcd_unitPrice = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='无税单价')
    prcd_sum = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='无税总额')
    po_identify = models.CharField(max_length=15, verbose_name='采购订单号')
    prq_identify = models.CharField(max_length=15, verbose_name='请购订单号')
    # prcd_remarks = models.TextField(max_length=200, verbose_name='采购入库单明细备注')

    class Meta:
        db_table = 'db_purchase_receipt_detail'
        verbose_name = "采购入库单明细"
        verbose_name_plural = verbose_name


class OtherPurchaseReceipt(models.Model):
    """ 其它入库单"""
    OPRC_TYPE_CHOICES = (
        (0, '转库入库'),
        (1, '盘盈出库'),
    )
    OPRC_STATUS_CHOICES = (
        (0, '草稿'),
        (1, '已审批')
    )
    id = models.AutoField(primary_key=True)
    oprc_identify = models.CharField(max_length=15, verbose_name='其它入库单编号')
    oprc_serial = models.CharField(max_length=4, verbose_name='其它入库单流水号')
    organization = models.ForeignKey('base.Organization', verbose_name='组织', related_name='org_oprc', on_delete=models.CASCADE)
    # transfer = models.OneToOneField('Transfer', verbose_name='转库单', on_delete=models.CASCADE)  # 如果不行保存为转库单identify
    # inventory = models.OneToOneField('Inventory', verbose_name='库存盘点单', on_delete=models.CASCADE)  # 同上
    oprc_wh = models.CharField(max_length=15, verbose_name='其它入库仓库名字')
    oprc_type = models.IntegerField(choices=OPRC_TYPE_CHOICES, verbose_name='其它入库单类型')
    oprc_date = models.DateField(auto_now_add=True, verbose_name='其它出库日期')
    oprc_remarks = models.TextField(max_length=400, verbose_name='其它出库单备注')
    oprc_status = models.IntegerField(choices=OPRC_STATUS_CHOICES, default=0, verbose_name='其它出库单状态')
    oprc_creator = models.CharField(max_length=20, verbose_name='其它出库单创建人')
    oprc_created_at = models.DateTimeField(auto_now_add=True, verbose_name='其它出库单创建日期')

    class Meta:
        db_table = 'db_other_purchase_receipt'
        verbose_name = "其它入库单"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.oprc_identify


class OtherPurchaseReceiptDetail(models.Model):
    """其它入库单明细"""
    id = models.AutoField(primary_key=True)
    other_prc = models.ForeignKey('OtherPurchaseReceipt', verbose_name='其它入库单', related_name='oprc_oprcd', on_delete=models.CASCADE)
    material = models.ForeignKey('base.Material', verbose_name='物料', related_name='material_oprcd', on_delete=models.CASCADE)
    oprcd_paper_num = models.IntegerField(verbose_name='应收数量')
    oprcd_real_num = models.IntegerField(verbose_name='实收数量')
    oprcd_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='无税单价')
    oprcd_sum = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='无税总额')

    class Meta:
        db_table = 'db_other_purchase_receipt_detail'
        verbose_name = "其它入库单详情"
        verbose_name_plural = verbose_name
