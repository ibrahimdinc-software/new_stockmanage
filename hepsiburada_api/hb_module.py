import datetime
import time

from .models import HepsiProductModel, UpdateStatusModel, HepsiOrderModel, HepsiOrderDetailModel, HepsiUpdateQueueModel, HepsiProductBuyBoxListModel, HepsiBillModel

from .hb_api import Listing, Order, Accounting

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

    def _getBuyBox(self, hpm, notif):
        if hpm.is_salable:            
            bbList = self.getBuyboxList(hpm.HepsiburadaSku)
            hpbblms = HepsiProductBuyBoxListModel.objects.filter(hpm=hpm)

            if bbList:
                for hpbblm in hpbblms:
                    hpbblm.delete()
                lastRank = hpm.buyBoxRank
                for bb in bbList:
                    hpbblm = HepsiProductBuyBoxListModel(
                        hpm=hpm,
                        rank=bb.get("Rank"),
                        merchantName=bb.get("MerchantName"),
                        price=bb.get("Price"),
                        dispatchTime=bb.get("DispatchTime")
                    )
                    hpbblm.save()
                
                    if bb.get("MerchantName") == "PetiFest":
                        hpm.buyBoxRank = bb.get("Rank")
                        hpm.save()

                if notif:
                    if lastRank != hpm.buyBoxRank:
                        return {
                            "status": "change",
                            "lastRank": lastRank, 
                            "currentRank": hpm.buyBoxRank,
                            "tpm": hpm.MerchantSku,
                            "url": "http://dev.petifest.com/admin/hepsiburada_api/hepsiproductmodel/{}/change/".format(hpm.id)
                        }
                    else:
                        return {
                            "status": "same"
                        }
                else:
                    time.sleep(.100)
                    return "{} -- Başarılı".format(hpm.MerchantSku)
            elif notif:
                return {
                    "status": "change",
                    "lastRank": "-", 
                    "currentRank": "-",
                    "tpm": hpm.MerchantSku,
                    "url": "HATALI"
                }
            else:
                return "{} -- Hata var!".format(hpm.MerchantSku)
        else:
            return "{} -- Satışta değil!!".format(hpm.MerchantSku)

    def buyboxList(self,hpms):
        messages = ""
        for hpm in hpms:
            messages += self._getBuyBox(hpm, False)
            messages += "\n"
        return messages

    def cronBuyBox(self):
        hpms = HepsiProductModel.objects.filter(is_salable=True)
        infos = []
        for hpm in hpms:
            m = self._getBuyBox(hpm, True)
            if m.get("status") == "change":
                infos.append(m)
        if len(infos) > 0:
            return infos
        return []

class OrderModule(Order):
    def __dateConverter__(self, date):
        return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')

    def __ifexist__(self,orders,orderNumber=None,packageNumber=None):
        for order in orders:
            if (orderNumber and order.get("orderNumber") == orderNumber) or (packageNumber and order.get("packageNumber") == packageNumber):
                return order
    
    def createOrder(self, orders):
        hepsiOrders = HepsiOrderModel.objects.all()
        hepsiProducts = HepsiProductModel.objects.all()

        for order in orders:
            if hepsiOrders.filter(orderNumber=order.get("orderNumber")):
                hom = hepsiOrders.get(orderNumber=order.get("orderNumber"))
                
                oDetails = hom.hepsiorderdetailmodel_set.all()

                for cod in order.get("details"):
                    if oDetails.filter(hpm=hepsiProducts.get(HepsiburadaSku=cod.get("hpm"))):
                        ood = oDetails.get(hpm=hepsiProducts.get(HepsiburadaSku=cod.get("hpm")))
                        ood.totalHbDiscount = float(cod.get("totalHbDiscount").replace('TRY','').replace(',','.')) if cod.get("totalHbDiscount") else 0
                        ood.priceToBilling = float(cod.get("priceToBilling").replace('TRY','').replace(',','.')) if cod.get("priceToBilling") else 0
                        ood.comission = float(cod.get("comission").replace('TRY','').replace(',','.')) if cod.get("comission") else 0
                        ood.save()
                        ood.setTotalPrice()
                    else:
                        hodm = HepsiOrderDetailModel(
                            hpm=hepsiProducts.get(HepsiburadaSku=cod.get("hpm")),
                            priceToBilling=float(cod.get("priceToBilling").replace('TRY','').replace(',','.')) if cod.get("priceToBilling") else 0,
                            hom=hom,
                            totalHbDiscount=float(cod.get("totalHbDiscount").replace('TRY','').replace(',','.')) if cod.get("totalHbDiscount") else 0,
                            quantity=cod.get("quantity"),
                            comission=float(cod.get("comission").replace('TRY','').replace(',','.')) if cod.get("comission") else 0
                        )
                        hodm.save()
                        hodm.setTotalPrice()
                hom.packageNumber = order.get("packageNumber")
                hom.status = order.get("status")
                hom.save()

                hom.setTotalPrice()

            else:
                hom = HepsiOrderModel(
                    customerName=order.get("customerName"),
                    orderNumber=order.get("orderNumber"),
                    packageNumber=order.get("packageNumber"),
                    orderDate=datetime.datetime.strptime(order.get("orderDate"), "%d-%m-%Y %H:%M:%S"),
                    status=order.get("status")
                )
                hom.save()
                
                for cod in order.get("details"):
                    hodm = HepsiOrderDetailModel(
                        hpm=hepsiProducts.get(HepsiburadaSku=cod.get("hpm")),
                        priceToBilling=float(cod.get("priceToBilling").replace('TRY','').replace(',','.')) if cod.get("priceToBilling") else 0,
                        hom=hom,
                        totalHbDiscount=float(cod.get("totalHbDiscount").replace('TRY','').replace(',','.')) if cod.get("totalHbDiscount") else 0,
                        quantity=cod.get("quantity"),
                        comission=float(cod.get("comission").replace('TRY','').replace(',','.')) if cod.get("comission") else 0
                    )
                    hodm.save()
                    hodm.setTotalPrice()
                
                hom.setPriceToBilling()
                hom.setTotalPrice()

    def getOldOrders(self, ordersFile):
        orders = []

        import pandas as pd

        data = pd.read_csv(ordersFile, sep=";")

        for d in data.iloc:
            order = None
            numConverter = lambda num: "0"+str(num) if str(num)[0] != "0" else str(num) if num else ''
            status = lambda stat: stat.get("Paket Durumu") if stat.get("Paket Durumu") !=None else stat.get("Durum")
            hpmFinder = lambda d: d.get("Hepsiburada Ürün Kodu") if d.get("Hepsiburada Ürün Kodu") != None else d.get("Ürün Numarası")

            if d.get("Sipariş Numarası"):
                order = self.__ifexist__(orders,orderNumber=d.get("Sipariş Numarası"))
            elif d.get("Paket Numarası"):
                order = self.__ifexist__(orders,packageNumber=d.get("Paket Numarası"))   
            
            if order:
                order["packageNumber"] = numConverter(d.get("Sipariş Numarası"))
                order["orderNumber"] = numConverter(d.get("Paket Numarası"))
                order["status"] = status(d)
                order["details"].append({
                        "hpm": hpmFinder(d),
                        "totalHbDiscount": d.get("HB'nin karşıladığı kampanya tutarı (KDV dahil)"),
                        "priceToBilling": d.get("Faturalandırılacak Satış Fiyatı"),
                        "quantity": d.get("Adet"),
                        "comission": d.get("Komisyon Tutarı (KDV Dahil)")
                    })
            else:
                orders.append({
                    "orderNumber": numConverter(d.get("Sipariş Numarası")),
                    "packageNumber": numConverter(d.get("Paket Numarası")),
                    "status": status(d),
                    "customerName": d.get("Alıcı"),
                    "orderDate": d.get("Sipariş Tarihi"),
                    "details": [{
                            "hpm": hpmFinder(d),
                            "totalHbDiscount": d.get("HB'nin karşıladığı kampanya tutarı (KDV dahil)"),
                            "priceToBilling": d.get("Faturalandırılacak Satış Fiyatı"),
                            "quantity": d.get("Adet"),
                            "comission": d.get("Komisyon Tutarı (KDV Dahil)")
                        }]
                    })

        self.createOrder(orders)
   
    def getOrders(self):
        orders = self.get()

        hepsiOrders = HepsiOrderModel.objects.all()
        hepsiProducts = HepsiProductModel.objects.all()

        for order in orders:
            if not hepsiOrders.filter(orderNumber=order.get("orderNumber")):
                date = self.__dateConverter__(order.get("orderDate"))
                hom = HepsiOrderModel(
                    customerName=order.get("name"),
                    orderNumber=order.get("orderNumber"),
                    orderDate=date,
                    status=order.get("status")
                )
                hom.save()

                details = self.getDetails(hom.orderNumber)

                for detail in details:
                    hodm = HepsiOrderDetailModel(
                        hom=hom,
                        priceToBilling=detail.get("priceToBilling"),
                        totalHbDiscount=detail.get("totalHbDiscount"),
                        hpm=hepsiProducts.get(HepsiburadaSku=detail.get("sku")),
                        quantity=detail.get("quantity")
                    )
                    hodm.save()
                    hodm.dropStock()

                    hodm.setTotalPrice()
            
                hom.setTotalPrice()
                hom.setPriceToBilling()

    def setPackageDetails(self):
        data = self.getPackageDetails()
        orders = HepsiOrderModel.objects.all()

        for d in data:
            if orders.filter(orderNumber=d.get("orderNumber")):
                order = orders.get(orderNumber=d.get("orderNumber"))
                order.packageNumber = d.get("packageNumber")
                order.save()
            else:
                order = HepsiOrderModel(
                    customerName=d.get("customerName"),
                    orderNumber=d.get("orderNumber"),
                    orderDate=self.__dateConverter__(d.get("orderDate")),
                    priceToBilling=d.get("priceToBilling"),
                    packageNumber=d.get("packageNumber"),
                    status=d.get("status")
                )
                order.save()
                for detail in d.get("detail"):
                    hodm = HepsiOrderDetailModel(
                        hpm=HepsiProductModel.objects.get(HepsiburadaSku=detail.get("hepsiBuradaSku")),
                        totalPrice=detail.get("totalPrice"),
                        priceToBilling=detail.get("priceToBilling"),
                        hom=order,
                        totalHbDiscount=detail.get("totalHbDiscount"),
                        quantity=detail.get("quantity")
                    )
                    hodm.save()
                    hodm.dropStock()

                order.setTotalPrice()
                order.setPriceToBilling()


class AccountingModule(Accounting):
    def getBills(self, obj):
        
        homs = HepsiOrderModel.objects.all()
        hpms = HepsiProductModel.objects.all()
        hbms = HepsiBillModel.objects.filter(hpm=obj)

        date = obj.date.strftime("%Y-%m-%d")

        dateConvert = lambda date: OrderModule().__dateConverter__(date) 
        numConverter = lambda num: "0"+str(num) if str(num)[0] != "0" else str(num) if num else ''

        from .models import TRANSACTION_TYPE

        if hbms:
            for hbm in hbms:
                hbm.delete() 

        for tType in TRANSACTION_TYPE:
            bills = self.get(tType=tType[0], endDate=date, startDate=date)

            for bill in bills:
                hom = None
                hodm = None

                if bill.get("orderNumber"):
                    hom = homs.filter(orderNumber=numConverter(bill.get("orderNumber"))).first()
                if not hom and bill.get("packageNumber"):
                    hom = homs.filter(packageNumber=numConverter(bill.get("packageNumber"))).first()

                if hom:
                    hodms = hom.hepsiorderdetailmodel_set.all()
                    hodm = hodms.get(hpm=hpms.get(HepsiburadaSku=bill.get("sku")))


                hbm = HepsiBillModel(
                        hpm=obj,
                        hodm=hodm,
                        hom=hom,
                        quantity=int(bill.get("quantity")),
                        totalAmount=float(bill.get("totalAmount").replace(',', '.')),
                        taxAmount=float(bill.get("taxAmount").replace(',', '.')),
                        netAmount=float(bill.get("netAmount").replace(',', '.')),
                        dueDate=dateConvert(bill.get("dueDate")),
                        invoiceDate=dateConvert(bill.get("invoiceDate")),
                        paymentDate=dateConvert(bill.get("paymentDate")),
                        invoiceNumber=bill.get("invoiceNumber"),
                        invoiceExplanation=bill.get("invoiceExplanation"),
                        transactionType=bill.get("transactionType")
                    )
                hbm.save()

