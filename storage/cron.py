from trendyol_api.tr_module import OrderModule as tr_Order
from hepsiburada_api.hb_module import OrderModule as hb_Order


def getOrders():
    print("Getir siparişleri moruk")
    tr_Order().getOrders()
    hb_Order().getOrders()