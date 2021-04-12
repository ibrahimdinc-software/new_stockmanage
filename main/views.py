from django.shortcuts import render
from django.views.generic import ListView

from datetime import date, datetime
import json

from .main_module import ProductModule
from marketplace.models import MarketOrderModel

# Create your views here.


def index(request):
    """
    context = {
        'unassigned': len(ProductModule().getUnassigned()),
        'unassignedHB': len(ProductModule().getUnassignedHB()),
        'unassignedTR': len(ProductModule().getUnassignedTR()),
        'losedBuyboxHB': len(ProductModule().getLosedBuyboxesHB()),
        'losedBuyboxTR': len(ProductModule().getLosedBuyboxesTR())
    }
    """

    statistics = MarketOrderModel.objects.getStatistics()

    context = {
        "dailySalesCount": statistics.get("dailySalesCount"),
        "dailySalesDifference": statistics.get("dailySalesDifference"),
        "dailySalesAmount": statistics.get("dailySalesAmount"),
        "dailySalesDifferenceAmount": statistics.get("dailySalesDifferenceAmount"),

        "weeklySalesCount": statistics.get("weeklySalesCount"),
        "weeklySalesDifference": statistics.get("weeklySalesDifference"),
        "weeklySalesAmount": statistics.get("weeklySalesAmount"),
        "weeklySalesDifferenceAmount": statistics.get("weeklySalesDifferenceAmount"),
        "weeklySalesGraph": json.dumps(statistics.get("weeklySalesGraph")),
    }
    return render(request, "main/index.html", context=context)


class UnassignedProductListView(ListView):
    template_name = "main/unassignedProductList.html"

    def get_queryset(self):
        return ProductModule().getUnassigned()


class UnassignedProductHBListView(ListView):
    template_name = "main/unassignedProductListHB.html"

    def get_queryset(self):
        return ProductModule().getUnassignedHB()


class UnassignedProductTRListView(ListView):
    template_name = "main/unassignedProductListTR.html"
    ordering = "name"

    def get_queryset(self):
        return ProductModule().getUnassignedTR()


class LosedBuyboxHBListView(ListView):
    template_name = "main/losedBuyboxHB.html"

    def get_queryset(self):
        return ProductModule().getLosedBuyboxesHB()


class LosedBuyboxTRListView(ListView):
    template_name = "main/losedBuyboxTR.html"

    def get_queryset(self):
        return ProductModule().getLosedBuyboxesTR()
