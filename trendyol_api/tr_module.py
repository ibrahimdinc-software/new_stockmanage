from datetime import datetime, timedelta

from .tr_api import Product, Order

from .models import TrendProductModel, TrendOrderModel, TrendOrderDetailModel

 
class ProductModule(Product):
    def getProducts(self):
        products = self.get()
        tpms = TrendProductModel.objects.all()
        if products:
            for p in products:
                print(p)
                print(type(p))
                tpm = tpms.filter(barcode=p.get("barcode"))
                if not tpm:
                    tpm = TrendProductModel(
                        barcode=p.get("barcode"),
                        name=p.get("title"),
                        listPrice=p.get("listPrice"),
                        piece=p.get("quantity"),
                        onSale=p.get("onSale"),
                        sku=p.get("stockCode"),
                        salePrice=p.get("salePrice")
                    )
                    tpm.save()
                else:
                    tpm = tpm[0]
                    
                    tpm.listPrice = p.get("listPrice")
                    tpm.salePrice = p.get("salePrice")
                    tpm.piece = p.get("quantity")
                    tpm.onSale = p.get("onSale")

                    tpm.save()
        else:
            return "Hata var lo!"

    def updateProducts(self, products):
        p_list = []
        for p in products:
            item={
                "barcode": p.barcode,
                "quantity": p.piece,
                "salePrice": p.salePrice,
                "listPrice": p.listPrice
            }
            print(item)
            p_list.append(item)
        result = self.update(p_list)
        print(result, "\n TR_MODULE.PY \n LINE:45")
        return self.batchControl(result)

    def dropStock(self, product, quantity):
        tmpms = product.trendmedproductmodel_set.all()
        for tmpm in tmpms:
            mpms = tmpm.product.medproductmodel_set.all()
            for mpm in mpms:
                mpm.base_product.dropStock(quantity)

class OrderModule(Order):
    def getOrders(self):
        orders = self.get()

        trendOrders = TrendOrderModel.objects.all()
        trendProducts = TrendProductModel.objects.all()

        for order in orders:
            if not trendOrders.filter(orderNumber=order.get("orderNumber")):
                print(order.get("orderDate"))
                date = datetime.fromtimestamp(order.get("orderDate")/1000)-timedelta(hours=3)
                print(date)
                tom = TrendOrderModel(
                    customerName=order["shipmentAddress"]["firstName"]+ " " + order["shipmentAddress"]["lastName"],
                    orderNumber=order.get("orderNumber"),
                    orderDate=date,
                    totalPrice=order.get("totalPrice")
                )
                tom.save()

                details = order.get("lines")

                for d in details:
                    todm = TrendOrderDetailModel(
                        tpm = trendProducts.get(sku=d.get("merchantSku"),barcode=d.get("sku")),
                        totalPrice= d.get("price"),
                        tom = tom,
                        quantity = d.get("quantity")
                    )
                    todm.save()

