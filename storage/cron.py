
from marketplace.module import ProductModule,OrderModule

from new_stockmanage.mail import loseBuyboxMail

def productUpdate():
    ProductModule().updateProducts()

def getOrders():
    OrderModule().getOrders()
    productUpdate()


def getBuyBoxes():
    infos = ProductModule().cronBuyBox()

    if len(infos) > 0:
        loseBuyboxMail(infos)

