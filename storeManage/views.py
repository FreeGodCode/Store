import json
from rest_framework.views import APIView
from rest_framework.response import Response
# from django.shortcuts import render
from base.models import UserNow
from . import models
from .serializer import TotalStockSerializer


class TotalStockView(APIView):

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

        total_stocks = models.TotalStock.objects.filter(totalwarehouse__organization__area_name=self.area_name)
        if total_stocks:
            total_stocks_serializer = TotalStockSerializer(total_stocks, many=True)
            return Response({"total_stocks": total_stocks_serializer.data})
        else:
            return Response({"message": "未查询到当地仓储信息"})
