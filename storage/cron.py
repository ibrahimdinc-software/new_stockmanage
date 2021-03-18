from trendyol_api.tr_module import OrderModule as tr_Order, ProductModule as tr_Product
from hepsiburada_api.hb_module import OrderModule as hb_Order, ProductModule as hb_Product

from new_stockmanage.mail import loseBuyboxMail

def productUpdate():
    hb_Product().updateProducts()
    tr_Product().updateProducts()

def getOrders():
    tr_Order().getOrders()
    hb_Order().getOrders()
    productUpdate()


def getBuyBoxes():
    infos = []
    infos += tr_Product().cronBuyBox()
    infos += hb_Product().cronBuyBox()

    if len(infos) > 0:
        loseBuyboxMail(infos)

