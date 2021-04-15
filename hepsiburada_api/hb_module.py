from billing.models import CustomerModel
import datetime
import time

from .models import HepsiProductModel, UpdateStatusModel, HepsiOrderModel, HepsiOrderDetailModel, HepsiBillModel

from .hb_api import Listing, HepsiOrderAPI, Accounting


class HepsiProductModule(Listing):
    def getHepsiProducts(self):
        products = self.getHepsiProductAPI()

        productList = []

        for p in products:
            onSale = True if p.get("IsSalable") == "true" else False

            productList.append({
                "marketType": "hepsiburada",
                "productName": p.get("ProductName"),
                "marketplaceSku": p.get("HepsiburadaSku"),
                "availableStock": p.get("AvailableStock"),
                "onSale": onSale,
                "sellerSku": p.get("MerchantSku"),
                "salePrice": p.get("Price"),
                "productLink": "https://www.hepsiburada.com/product-p-"+str(p.get("HepsiburadaSku")),
                "DispatchTime": p.get("DispatchTime"),
                "CargoCompany1": p.get("CargoCompany1"),
                "CargoCompany2": p.get("CargoCompany2"),
                "CargoCompany3": p.get("CargoCompany3"),
            })
        return productList

    def updateHepsiProducts(self, hpms):
        l = []
        hepsiProductModels = HepsiProductModel.objects.all()
        if hpms:
            for hpm in hpms:
                hpm = hepsiProductModels.get(id=hpm.id)
                d = {
                    "HepsiburadaSku": hpm.marketplaceSku,
                    "MerchantSku": hpm.sellerSku,
                    "ProductName": hpm.productName,
                    "Price": hpm.get_price(),
                    "AvailableStock": hpm.availableStock,
                    "DispatchTime": hpm.DispatchTime,
                    "CargoCompany1": hpm.CargoCompany1,
                }
                l.append(d)

            response = self.update(l)
            self.createUpdateControl(response.get("Id"))

    def createUpdateControl(self, id):
        usm = UpdateStatusModel(control_id=id)
        usm.save()

    def updateControl(self, id):
        response = Listing().controlListing(id)
        if response.get("Errors"):
            return "Hata var kontrol et!"
        return "Oha gerçekten nasıl başarılı olabilir ya?"

    def _getHepsiBuyBox(self, mpm):
        bbList = []

        for bb in self.getHepsiBuyboxList(mpm.marketplaceSku):
            bbList.append({
                "rank": bb.get("Rank"),
                "merchantName": bb.get("MerchantName"),
                "price": bb.get("Price"),
                "dispatchTime": bb.get("DispatchTime")
            })
        return bbList


class HepsiOrderModule(HepsiOrderAPI):
    def __dateConverter__(self, date):
        return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')

    def __ifexist__(self, orders, orderNumber=None, packageNumber=None):
        for order in orders:
            if (orderNumber and order.get("orderNumber") == orderNumber) or (packageNumber and order.get("packageNumber") == packageNumber):
                return order


    def getHepsiOrders(self):
        orders = self.hepsiGet()

        hepsiOrders = HepsiOrderModel.objects.all()
        hepsiProducts = HepsiProductModel.objects.all()

        for order in orders:
            customer, customerData = CustomerModel.objects.get_or_create(name=order["name"])
            
            customerData = order["shippingAddress"]
            customerData["taxId"] = ""
            customerData["mail"] = customerData["email"]
            customerData["phone"] = customerData["phoneNumber"]
            customerData["district"] = customerData["town"]
            customerData["fullAddress"] = customerData["address"]

            hom = hepsiOrders.filter(orderNumber=order.get("orderNumber"))
            if not hom:
                date = self.__dateConverter__(order.get("orderDate"))
                hom = HepsiOrderModel(
                    marketType="hepsiburada",
                    orderNumber=order.get("orderNumber"),
                    orderDate=date,
                    orderStatus=order.get("status")
                )
                hom.save()
                
                hom.setCustomer(customer, customerData)

                details = self.getDetails(hom.orderNumber)

                for detail in details:
                    hodm = HepsiOrderDetailModel(
                        mom=hom,
                        priceToBilling=detail.get("priceToBilling"),
                        totalHbDiscount=detail.get("totalHbDiscount"),
                        mpm=hepsiProducts.get(
                            marketplaceSku=detail.get("sku")),
                        quantity=detail.get("quantity")
                    )
                    hodm.save()
                    hodm.dropStock()

                    hodm.setTotalPrice()

                hom.setTotalPrice()
                hom.setPriceToBilling()
            else:
                hom = hom.first()
                hom.setCustomer(customer, customerData)
            


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
                    orderNumber=d.get("orderNumber"),
                    orderDate=self.__dateConverter__(d.get("orderDate")),
                    priceToBilling=d.get("priceToBilling"),
                    packageNumber=d.get("packageNumber"),
                    status=d.get("status")
                )
                order.save()
                for detail in d.get("detail"):
                    hodm = HepsiOrderDetailModel(
                        mpm=HepsiProductModel.objects.get(
                            marketplaceSku=detail.get("marketplaceSku")),
                        totalPrice=detail.get("totalPrice"),
                        priceToBilling=detail.get("priceToBilling"),
                        mom=order,
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

        def dateConvert(date): return HepsiOrderModule(
        ).__dateConverter__(date)

        def numConverter(num): return "0" + \
            str(num) if str(num)[0] != "0" else str(num) if num else ''

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
                    hom = homs.filter(orderNumber=numConverter(
                        bill.get("orderNumber"))).first()
                if not hom and bill.get("packageNumber"):
                    hom = homs.filter(packageNumber=numConverter(
                        bill.get("packageNumber"))).first()

                if hom:
                    hodms = hom.marketorderdetailmodel_set.all()
                    hodm = hodms.get(mpm=hpms.get(
                        marketplaceSku=bill.get("sku")))

                hbm = HepsiBillModel(
                    hpm=obj,
                    hodm=hodm,
                    hom=hom,
                    quantity=int(bill.get("quantity")),
                    totalAmount=float(
                        bill.get("totalAmount").replace(',', '.')),
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
