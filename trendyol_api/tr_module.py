from datetime import datetime, timedelta

from .tr_api import TrendProductAPI, TrendOrderAPI

from .models import TrendProductModel, TrendOrderModel

 
class TrendProductModule(TrendProductAPI):
    def getTrendProducts(self):
        products = self.getTrendProductAPI()
        tpms = TrendProductModel.objects.all()
        if products:
            for p in products:
                tpm = tpms.filter(marketplaceSku=p.get("barcode"))
                if not tpm:
                    tpm = TrendProductModel(
                        marketplaceSku=p.get("barcode"),
                        productName=p.get("title"),
                        listPrice=p.get("listPrice"),
                        availableStock=p.get("quantity"),
                        onSale=p.get("onSale"),
                        sellerSku=p.get("stockCode"),
                        salePrice=p.get("salePrice"),
                        productLink="https://www.trendyol.com/marka/urun-p-"+str(p.get("productContentId"))
                    )
                    tpm.save()
                else:
                    tpm = tpm[0]
                    
                    tpm.listPrice = p.get("listPrice")
                    tpm.salePrice = p.get("salePrice")
                    tpm.availableStock = p.get("quantity")
                    tpm.onSale = p.get("onSale")
                    tpm.productLink = "https://www.trendyol.com/marka/urun-p-"+str(p.get("productContentId")) if p.get("productContentId") != None else "ContentId Not Found!"

                    tpm.save()
        else:
            return "Hata var lo!"

    def updateTrendProducts(self, tpms):
        l = []
        if tpms:
            for tpm in tpms:
                item={
                    "barcode": tpm.marketplaceSku,
                    "quantity": tpm.availableStock,
                    "salePrice": tpm.salePrice,
                    "listPrice": tpm.listPrice
                }
                l.append(item)

            result = self.update(l)
            
            return self.batchControl(result)

    #! Add update control methods

    def _getTrendBuyBox(self, mpm):
        return self.getTrendBuyboxList(mpm.productLink)


class TrendOrderModule(TrendOrderAPI):
    def getTrendOrders(self):
        orders = self.get("Awaiting,Created,Picking,Invoiced")

        trendOrders = TrendOrderModel.objects.all()
        trendProducts = TrendProductModel.objects.all()

        for order in orders:
            if not trendOrders.filter(orderNumber=order.get("orderNumber")):
                date = datetime.fromtimestamp(order.get("orderDate")/1000)-timedelta(hours=3)
                tom = TrendOrderModel(
                    customerName=order["shipmentAddress"]["firstName"]+ " " + order["shipmentAddress"]["lastName"],
                    packageNumber=order.get("id"),
                    orderNumber=order.get("orderNumber"),
                    orderDate=date,
                    totalPrice=order.get("grossAmount"),
                    priceToBilling=order.get("totalPrice"),
                    orderStatus=order.get("shipmentPackageStatus")
                )
                tom.save()

                details = order.get("lines")

                from marketplace.models import MarketOrderDetailModel

                for d in details:
                    todm = MarketOrderDetailModel(
                        mpm = trendProducts.get(marketplaceSku=d.get("sku")),
                        totalPrice= d.get("price"),
                        mom = tom,
                        quantity = d.get("quantity")
                    )
                    todm.save()
                    todm.dropStock()

    def getOldOrders(self, startDate):
        pass
