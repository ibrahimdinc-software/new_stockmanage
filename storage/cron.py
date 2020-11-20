from trendyol_api.tr_module import OrderModule as tr_Order, ProductModule as tr_Product
from hepsiburada_api.hb_module import OrderModule as hb_Order, ListingModule as hb_Listing


def productUpdate():
    hb_Listing().sendProducts()
    tr_Product().updateProducts()

def getOrders():
    tr_Order().getOrders()
    hb_Order().getOrders()
    productUpdate()