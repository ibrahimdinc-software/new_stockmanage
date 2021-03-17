from datetime import datetime, timedelta

from .tr_api import Product, Order

from .models import TrendProductModel, TrendOrderModel, TrendOrderDetailModel, TrendUpdateQueueModel, TrendProductBuyBoxListModel

 
class ProductModule(Product):
    def getProducts(self):
        products = self.get()
        tpms = TrendProductModel.objects.all()
        if products:
            for p in products:
                tpm = tpms.filter(barcode=p.get("barcode"))
                if not tpm:
                    tpm = TrendProductModel(
                        barcode=p.get("barcode"),
                        name=p.get("title"),
                        listPrice=p.get("listPrice"),
                        piece=p.get("quantity"),
                        onSale=p.get("onSale"),
                        sku=p.get("stockCode"),
                        salePrice=p.get("salePrice"),
                        productLink="https://www.trendyol.com/marka/urun-p-"+str(p.get("productContentId"))
                    )
                    tpm.save()
                else:
                    tpm = tpm[0]
                    
                    tpm.listPrice = p.get("listPrice")
                    tpm.salePrice = p.get("salePrice")
                    tpm.piece = p.get("quantity")
                    tpm.onSale = p.get("onSale")
                    tpm.productLink = "https://www.trendyol.com/marka/urun-p-"+str(p.get("productContentId")) if p.get("productContentId") != None else "ContentId Not Found!"

                    if p.get("productContentId") == None:
                        print(p.get("barcode"))

                    tpm.save()
        else:
            return "Hata var lo!"

    def updateQueue(self, qs):
        tuqMs = TrendUpdateQueueModel.objects.all()
        if not 'count' in dir(qs):
            if not tuqMs.filter(tpm=qs):
                tuq = TrendUpdateQueueModel(tpm=qs)
                tuq.save()
        elif qs.count() > 1:
            for p in qs:
                if not tuqMs.filter(tpm=p):
                    tuq = TrendUpdateQueueModel(tpm=p)
                    tuq.save()
        else:
            if not tuqMs.filter(tpm=qs[0]):
                tuq = TrendUpdateQueueModel(tpm=qs[0])
                tuq.save()

    def updateProducts(self):
        p_list = []
        tuqs = TrendUpdateQueueModel.objects.all()
        if tuqs:
            for tuq in tuqs:
                p = tuq.tpm
                item={
                    "barcode": p.barcode,
                    "quantity": p.piece,
                    "salePrice": p.salePrice,
                    "listPrice": p.listPrice
                }
                p_list.append(item)
                tuq.delete()
            result = self.update(p_list)
            print(result, "\n TR_MODULE.PY \n LINE:45")
            return self.batchControl(result)

    def dropStock(self, product, quantity):
        tmpms = product.trendmedproductmodel_set.all()
        for tmpm in tmpms:
            mpms = tmpm.product.medproductmodel_set.all()
            for mpm in mpms:
                mpm.base_product.dropStock(quantity*mpm.piece)

    def increaseStock(self, product, quantity):
        tmpms = product.trendmedproductmodel_set.all()
        for tmpm in tmpms:
            mpms = tmpm.product.medproductmodel_set.all()
            for mpm in mpms:
                mpm.base_product.increaseStock(quantity*mpm.piece)

    #! Add update control methods


    def buyboxList(self,tpms):
        for tpm in tpms:
            if tpm.onSale:            
                bbList = self.getBuyboxList(tpm.productLink)
                tpbblms = TrendProductBuyBoxListModel.objects.filter(tpm=tpm)

                if bbList:
                    for tpbblm in tpbblms:
                        tpbblm.delete()

                    for bb in bbList:
                        tpbblm = TrendProductBuyBoxListModel(
                            tpm=tpm,
                            rank=bb.get("rank"),
                            merchantName=bb.get("merchantName"),
                            price=bb.get("price"),
                        )
                        tpbblm.save()

                        if bb.get("merchantName") == "PetiFest":
                            tpm.buyBoxRank = bb.get("rank")
                            tpm.save()

                    return None 
                else:
                    return "Hata var!"
            else:
                return "Satışta olmayan bir ürünün buybox bilgilerini getiremem ki :/"
        return "Bitti ?"

           


class OrderModule(Order):
    def getOrders(self):
        orders = self.get("Awaiting,Created,Picking,Invoiced")

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
                    totalPrice=order.get("totalPrice"),
                    orderStatus=order.get("shipmentPackageStatus")
                )
                tom.save()

                details = order.get("lines")

                for d in details:
                    todm = TrendOrderDetailModel(
                        tpm = trendProducts.get(barcode=d.get("sku")),
                        totalPrice= d.get("price"),
                        tom = tom,
                        quantity = d.get("quantity")
                    )
                    todm.save()
                    todm.dropStock()

    def getOldOrders(self, startDate):
        pass
