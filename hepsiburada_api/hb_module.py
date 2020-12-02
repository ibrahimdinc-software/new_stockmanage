import datetime

from .models import HepsiProductModel, UpdateStatusModel, HepsiOrderModel, HepsiOrderDetailModel, HepsiUpdateQueueModel, HepsiProductBuyBoxListModel

from .hb_api import Listing, Order

class ProductModule(Listing):
    def getProducts(self):
        listings = self.get()
        objs = HepsiProductModel.objects.all()
        for listing in listings:
            obj = objs.filter(HepsiburadaSku=listing.get("HepsiburadaSku"))
            if not obj:
                is_salable = True if listing.get("IsSalable")=="true" else False
                obj = HepsiProductModel(
                    HepsiburadaSku=listing.get("HepsiburadaSku"),
                    MerchantSku=listing.get("MerchantSku"),
                    ProductName=listing.get("ProductName"),
                    Price=listing.get("Price"),
                    AvailableStock=listing.get("AvailableStock"),
                    DispatchTime=listing.get("DispatchTime"),
                    CargoCompany1=listing.get("CargoCompany1"),
                    CargoCompany2=listing.get("CargoCompany2"),
                    CargoCompany3=listing.get("CargoCompany3"),
                    is_salable=is_salable
                )
                obj.save()
            else:
                obj = obj[0]

                is_salable = True if listing.get("IsSalable")=="true" else False
                obj.MerchantSku = listing.get("MerchantSku")
                obj.Price = listing.get("Price")
                obj.AvailableStock = listing.get("AvailableStock")
                obj.is_salable=is_salable

                obj.save()

    def updateQueue(self, qs):
        huqMs = HepsiUpdateQueueModel.objects.all()
        if not 'count' in dir(qs):
            if not huqMs.filter(hpm=qs):
                huq = HepsiUpdateQueueModel(hpm=qs)
                huq.save()
        elif qs.count() > 1:
            for p in qs:
                if not huqMs.filter(hpm=p):
                    huq = HepsiUpdateQueueModel(hpm=p)
                    huq.save()
        else:
            if not huqMs.filter(hpm=qs[0]):
                huq = HepsiUpdateQueueModel(hpm=qs[0])
                huq.save()

    def updateProducts(self):
        l = []
        huqs = HepsiUpdateQueueModel.objects.all()
        if huqs:
            for huq in huqs:
                p = huq.hpm
                d = {
                    "HepsiburadaSku": p.HepsiburadaSku,
                    "MerchantSku": p.MerchantSku,
                    "ProductName": p.ProductName,
                    "Price": p.get_price(),
                    "AvailableStock": p.AvailableStock,
                    "DispatchTime": p.DispatchTime,
                    "CargoCompany1": p.CargoCompany1,
                }
                l.append(d)
                huq.delete()

            response = self.update(l)
            self.createUpdateControl(response.get("Id"))

    def dropStock(self, product, quantity):
        hmpms = product.hepsimedproductmodel_set.all()
        for hmpm in hmpms:
            mpms = hmpm.product.medproductmodel_set.all()
            for mpm in mpms:
                mpm.base_product.dropStock(quantity*mpm.piece)

    def increaseStock(self, product, quantity):
        hmpms = product.hepsimedproductmodel_set.all()
        for hmpm in hmpms:
            mpms = hmpm.product.medproductmodel_set.all()
            for mpm in mpms:
                mpm.base_product.increaseStock(quantity*mpm.piece)

    def createUpdateControl(self, id):
        usm = UpdateStatusModel(control_id=id)
        usm.save()

    def updateControl(self, id):
        response = Listing().controlListing(id)
        if response.get("Errors"):
            return "Hata var kontrol et!"
        return "Oha gerçekten nasıl başarılı olabilir ya?"

    def buyboxList(self,hpm):
        if hpm.is_salable:            
            bbList = self.getBuyboxList(hpm.HepsiburadaSku)
            hpbblms = HepsiProductBuyBoxListModel.objects.filter(hpm=hpm)

            notSelling = []
            if bbList:
                for bb in bbList:
                    hpbblm = hpbblms.filter(merchantName=bb.get("MerchantName"))
                    if hpbblm:
                        hpbblm = hpbblm[0]
                        hpbblm.rank = bb.get("Rank")
                        hpbblm.merchantName = bb.get("MerchantName")
                        hpbblm.price = bb.get("Price")
                        hpbblm.dispatchTime = bb.get("DispatchTime")
                        hpbblm.save()
                    elif not hpbblm:
                        hpbblm = HepsiProductBuyBoxListModel(
                            hpm=hpm,
                            rank=bb.get("Rank"),
                            merchantName=bb.get("MerchantName"),
                            price=bb.get("Price"),
                            dispatchTime=bb.get("DispatchTime")
                        )
                        hpbblm.save()
                    else:
                        notSelling.append(hpbblm[0])

                    if bb.get("MerchantName") == "Meow Meow":
                        hpm.buyBoxRank = bb.get("Rank")
                        hpm.save()
                
                for i in notSelling:
                    i.delete()
                return None 
            else:
                return "Hata var!"
        else:
            return "Satışta olmayan bir ürünün buybox bilgilerini getiremem ki :/"   

class OrderModule(Order):
    def __dateConverter__(self, date):
        return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')

    def getOrders(self):
        orders = self.get()

        hepsiOrders = HepsiOrderModel.objects.all()
        hepsiProducts = HepsiProductModel.objects.all()

        for order in orders:
            if not hepsiOrders.filter(orderNumber=order.get("orderNumber")):
                date = self.__dateConverter__(order.get("orderDate"))
                hom = HepsiOrderModel(
                    hepsiId=order.get("orderId"),
                    customerName=order.get("name"),
                    orderNumber=order.get("orderNumber"),
                    orderDate=date,
                    totalPrice=float(order.get("totalPrice"))
                )
                hom.save()

                details = self.getDetails(hom.orderNumber)

                for detail in details:
                    hodm = HepsiOrderDetailModel(
                        hom=hom,
                        totalPrice=detail.get("totalPrice"),
                        hpm=hepsiProducts.get(HepsiburadaSku=detail.get("sku")),
                        quantity=detail.get("quantity")
                    )
                    hodm.save()
                    hodm.dropStock()



