
from marketplace.module import ProductModule,OrderModule

from new_stockmanage.mail import loseBuyboxMail

def productUpdate():
    ProductModule().updateProducts()

def getOrders():
    OrderModule().getOrders()
    productUpdate()

def getDeliverdOrders():
    OrderModule().getDeliveredOrders()

def getBuyBoxes():
    infos = ProductModule().cronBuyBox()


