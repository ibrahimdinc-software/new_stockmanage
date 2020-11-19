import datetime

from .models import HepsiProductModel, UpdateStatusModel, HepsiOrderModel, HepsiOrderDetailModel

from .hb_api import Listing, Order

class ListingModule:
    def createListingUpdateControl(self, id):
        usm = UpdateStatusModel(control_id=id)
        usm.save()

    def listingUpdateControl(self, id):
        response = Listing().controlListing(id)
        if response.get("Errors"):
            return "Hata var kontrol et!"
        return "Oha gerçekten nasıl başarılı olabilir ya?"

    def createProducts(self):
        listings = Listing().getListing()
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
                obj.Price = listing.get("Price")
                obj.AvailableStock = listing.get("AvailableStock")
                obj.is_salable=is_salable

                obj.save()


    def dropStock(self, product, quantity):
        hmpms = product.hepsimedproductmodel_set.all()
        for hmpm in hmpms:
            mpms = hmpm.product.medproductmodel_set.all()
            for mpm in mpms:
                mpm.base_product.dropStock(quantity)

    def sendProducts(self, qs):
        d=[]
        if not 'count' in dir(qs):
            d = {
                "HepsiburadaSku": qs.HepsiburadaSku,
                "MerchantSku": qs.MerchantSku,
                "ProductName": qs.ProductName,
                "Price": qs.get_price(),
                "AvailableStock": int(qs.AvailableStock),
                "DispatchTime": qs.DispatchTime,
                "CargoCompany1": qs.CargoCompany1,
            }
        elif qs.count() > 1:
            for p in qs:
                d.append({
                    "HepsiburadaSku": p.HepsiburadaSku,
                    "MerchantSku": p.MerchantSku,
                    "ProductName": p.ProductName,
                    "Price": p.get_price(),
                    "AvailableStock": p.AvailableStock,
                    "DispatchTime": p.DispatchTime,
                    "CargoCompany1": p.CargoCompany1,
                })
        else:
            d = {
                "HepsiburadaSku": qs[0].HepsiburadaSku,
                "MerchantSku": qs[0].MerchantSku,
                "ProductName": qs[0].ProductName,
                "Price": qs[0].get_price(),
                "AvailableStock": qs[0].AvailableStock,
                "DispatchTime": qs[0].DispatchTime,
                "CargoCompany1": qs[0].CargoCompany1,
            }

        response = Listing().updateListing(d)
        self.createListingUpdateControl(response.get("Id"))

    def deleteAll(self, qs):
        lis = []
        for p in qs:
            d = {
                "hbSku": p.HepsiburadaSku,
                "merchSku": p.MerchantSku
            }
            p.delete()
            lis.append(d)
        Listing().deleteProducts(lis)


class OrderModule:
    def getOrders(self):
        orders = Order().get_orders()

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

                details = Order().get_order_details(hom.orderNumber)

                for detail in details:
                    hodm = HepsiOrderDetailModel(
                        hom=hom,
                        totalPrice=detail.get("totalPrice"),
                        hpm=hepsiProducts.get(HepsiburadaSku=detail.get("sku")),
                        quantity=detail.get("quantity")
                    )
                    hodm.save()








    def __dateConverter__(self, date):
        print(date)
        return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')

