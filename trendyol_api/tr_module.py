from datetime import datetime, timedelta

from .tr_api import Product, Order

from .models import TrendProductModel, TrendOrderModel, TrendOrderDetailModel, TrendUpdateQueueModel, TrendProductBuyBoxListModel

 
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

    def buyboxList(self,tpm):
        if tpm.onSale:            
            bbList = self.getBuyboxList(tpm.HepsiburadaSku)
            tpbblms = TrendProductBuyBoxListModel.objects.filter(tpm=tpm)

            notSelling = []
            if bbList:
                for bb in bbList:
                    tpbblm = tpbblms.filter(merchantName=bb.get("MerchantName"))
                    if tpbblm:
                        tpbblm = tpbblm[0]
                        tpbblm.rank = bb.get("Rank")
                        tpbblm.merchantName = bb.get("MerchantName")
                        tpbblm.price = bb.get("Price")
                        tpbblm.dispatchTime = bb.get("DispatchTime")
                        tpbblm.save()
                    elif not tpbblm:
                        tpbblm = TrendProductBuyBoxListModel(
                            tpm=tpm,
                            rank=bb.get("Rank"),
                            merchantName=bb.get("MerchantName"),
                            price=bb.get("Price"),
                            dispatchTime=bb.get("DispatchTime")
                        )
                        tpbblm.save()
                    else:
                        notSelling.append(tpbblm[0])

                    if bb.get("MerchantName") == "Meow Meow":
                        tpm.buyBoxRank = bb.get("Rank")
                        tpm.save()
                
                for i in notSelling:
                    i.delete()
                return None 
            else:
                return "Hata var!"
        else:
            return "Satışta olmayan bir ürünün buybox bilgilerini getiremem ki :/"   


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
