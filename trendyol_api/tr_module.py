from datetime import datetime, time, timedelta

from .tr_api import TrendProductAPI, TrendOrderAPI

from billing.models import CustomerModel
from .models import TrendProductModel, TrendOrderModel

 
class TrendProductModule(TrendProductAPI):
    def getTrendProducts(self):
        products = self.getTrendProductAPI()

        productList = []

        for p in products:
            productList.append({
                "marketType": "trendyol",
                "productName": p.get("title"),
                "marketplaceSku": p.get("barcode"),
                "listPrice": p.get("listPrice"),
                "availableStock": p.get("quantity"),
                "onSale": p.get("onSale"),
                "sellerSku": p.get("stockCode"),
                "salePrice": p.get("salePrice"),
                "productLink": "https://www.trendyol.com/marka/urun-p-"+str(p.get("productContentId")) if p.get("productContentId") != None else "ContentId Not Found!"
            })

        return productList


    def updateTrendProducts(self, tpms):
        l = []
        trendProductModels = TrendProductModel.objects.all()
        if tpms:
            for tpm in tpms:
                tpm = trendProductModels.get(id=tpm.id)
                item={
                    "barcode": tpm.marketplaceSku,
                    "quantity": tpm.availableStock,
                    "salePrice": tpm.salePrice,
                    "listPrice": tpm.listPrice
                }
                l.append(item)

            result = self.trendUpdate(l)
            
            return self.batchControl(result)

    #! Add update control methods

    def _getTrendBuyBox(self, mpm):
        bbList = []

        for bb in self.getTrendBuyboxList(mpm.productLink):
            bbList.append({
                "rank": bb.get("rank"),
                "merchantName": bb.get("merchantName"),
                "price": bb.get("price")
            })
        return bbList


class TrendOrderModule(TrendOrderAPI):
    def getTrendOrders(self):
        orders = self.get("Awaiting,Created,Picking,Invoiced,Cancelled,Shipped")

        trendOrders = TrendOrderModel.objects.all()
        trendProducts = TrendProductModel.objects.all()

        for order in orders:
            customer, customerData = CustomerModel.objects.get_or_create(name=order["shipmentAddress"]["fullName"])
            if not customerData:
                customerData = order["shipmentAddress"]
                customerData["taxId"] = order["taxNumber"]
                customerData["mail"] = order["customerEmail"]

            to = None
            if not trendOrders.filter(orderNumber=order.get("orderNumber")):
                to = self.createTrendOrder(trendProducts, order)
            else:
                to = trendOrders.filter(orderNumber=order.get("orderNumber")).first()
                to.orderStatus = order.get("shipmentPackageStatus")
            
            to.save()
            to.setCustomer(customer, customerData)


            if order.get("shipmentPackageStatus") == "Cancelled":
                to = trendOrders.filter(orderNumber=order.get("orderNumber"))
                if to:
                    to = to.first()
                    if to.orderStatus != "Cancelled":
                        to.canceledOrder()

    def getOldTrendOrders(self, date):
        currentDate = int(datetime.timestamp(datetime.now())*1000)
        date = int(datetime.timestamp(datetime.strptime(date, "%Y-%m-%d"))*1000)

        fourteenDays = 1209600000
        endDate = date + fourteenDays


        while True:
            orders = self.get("Shipped,Delivered,UnDelivered,Returned,Repack,UnPacked,UnSupplied,Cancelled", date, endDate)
            
            trendOrders = TrendOrderModel.objects.all()
            trendProducts = TrendProductModel.objects.all()


            for order in orders:
                customer, customerData = CustomerModel.objects.get_or_create(name=order["shipmentAddress"]["fullName"])
                if not customerData:
                    customerData = order["shipmentAddress"]
                    customerData["taxId"] = order["taxNumber"]
                    customerData["mail"] = order["customerEmail"]

                tom = None
                if not trendOrders.filter(orderNumber=order.get("orderNumber")):
                    tom = self.createTrendOrder(trendProducts, order, dropStock=False)
                else:
                    tom = trendOrders.filter(orderNumber=order.get("orderNumber")).first()
                    tom.orderStatus = order.get("shipmentPackageStatus")

                    if order.get("shipmentPackageStatus") == "Delivered":
                        self.setDeliveryDate(tom, order.get("packageHistories"))

                tom.save()
                tom.setUserMarket("trendyol")
                tom.setCustomer(customer, customerData)

            if endDate > currentDate:
                break
            date = endDate
            endDate = date + fourteenDays

    def getDeliveredTrendOrders(self):
        notDeliveredTrendOrders = TrendOrderModel.objects.filter(deliveryDate__isnull = True).order_by("orderDate")

        for trendOrder in notDeliveredTrendOrders:
            order = self.get(orderNumber=trendOrder.orderNumber)[0]

            trendOrder.orderStatus = order.get("shipmentPackageStatus")
            trendOrder.save()

            self.setDeliveryDate(trendOrder, order.get("packageHistories"))
            
            time.sleep(100)
            


    def createTrendOrder(self, trendProducts, order, dropStock=True):
        date = datetime.fromtimestamp(order.get("orderDate")/1000)-timedelta(hours=3)
        tom = TrendOrderModel(
            packageNumber=order.get("id"),
            orderNumber=order.get("orderNumber"),
            orderDate=date,
            totalPrice=order.get("grossAmount"),
            priceToBilling=order.get("totalPrice"),
            orderStatus=order.get("shipmentPackageStatus")
        )
        tom.save()
        tom.setUserMarket("trendyol")

        if order.get("status") == "Delivered":
            self.setDeliveryDate(tom, order.get("packageHistories"))

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
            if dropStock:
                todm.dropStock() 

        return tom

    def setDeliveryDate(self, order, packageHistories):
        deliveryDate = None 
        for packageHistory in packageHistories:
            if packageHistory.get("status") == "Delivered":
                deliveryDate = packageHistory.get("createdDate")
                break
        
        order.deliveryDate = datetime.fromtimestamp(deliveryDate/1000)
        print(order)
        order.save()

