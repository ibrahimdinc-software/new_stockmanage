from billing.models import CustomerModel
import datetime
import pandas as pd

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
                "productName": p.get("productName"),
                "marketplaceSku": p.get("hepsiburadaSku"),
                "availableStock": p.get("availableStock"),
                "onSale": onSale,
                "sellerSku": p.get("merchantSku"),
                "salePrice": p.get("price"),
                "productLink": "https://www.hepsiburada.com/product-p-"+str(p.get("hepsiburadaSku")),
                "commissionRate": p.get("commissionRate"),
                "DispatchTime": p.get("dispatchTime"),
                "CargoCompany1": p.get("cargoCompany1"),
                "CargoCompany2": p.get("cargoCompany2"),
                "CargoCompany3": p.get("cargoCompany3"),
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
                    "Price": hpm.get_price(),
                    "AvailableStock": hpm.availableStock,
                    "DispatchTime": hpm.DispatchTime,
                    "CargoCompany1": hpm.CargoCompany1,
                    "CargoCompany2": hpm.CargoCompany2,
                }
                l.append(d)

            response = self.update(l)
            self.createUpdateControl(response["id"])

    def createUpdateControl(self, id):
        usm = UpdateStatusModel(control_id=id)
        usm.save()

    def updateControl(self, id):
        response = self.controlListing(id)
        if response.get("errors"):
            return response.get("errors")
        return "Oha gerçekten nasıl başarılı olabilir ya?"

    def _getHepsiBuyBox(self, mpm):
        bbList = []
        data = self.getHepsiBuyboxList(mpm.marketplaceSku)
        if data:
            for bb in data:
                bbList.append({
                    "rank": bb.get("rank"),
                    "merchantName": bb.get("merchantName"),
                    "price": bb.get("price"),
                    "dispatchTime": bb.get("dispatchTime")
                })
        return bbList


class HepsiOrderModule(HepsiOrderAPI):
    def __dateConverter__(self, date):
        return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')

    def __ifexist__(self, orders, orderNumber=None, packageNumber=None):
        for order in orders:
            if (orderNumber and order.get("orderNumber") == orderNumber) or (packageNumber and order.get("packageNumber") == packageNumber):
                return order

    def getHepsiOldOrders(self, data):
        hepsiOrders = HepsiOrderModel.objects.all()
        hepsiProducts = HepsiProductModel.objects.all()

        orders = pd.read_csv(data, ";").to_numpy()

        for order in orders:
            customer, customerData = CustomerModel.objects.get_or_create(name=order[9])
            customerData = {
                "taxId" : "",
                "mail": order[36] if order[36] else "",
                "phone": "",
                "district": "",
                "fullAddress": order[31]
            }

            hom = hepsiOrders.filter(orderNumber=order[7])
            if not hom:
                hom = HepsiOrderModel(
                    orderNumber=order[7],
                    orderDate=datetime.datetime.strptime(order[3], '%d-%m-%Y %H:%M:%S'),
                    orderStatus=order[32]
                )
                hom.save()
                hom.setUserMarket("hepsiburada")

            else:
                hom = hom.first()

            hodm, creeated = HepsiOrderDetailModel.objects.get_or_create(
                mom=hom,
                priceToBilling=float(order[23].replace("TRY","").replace(",",".")),
                totalHbDiscount=float(order[25].replace("TRY","").replace(",",".")),
                mpm=hepsiProducts.get(marketplaceSku=order[13]),
                quantity=order[21],
                commissionRate=100*float(order[24].replace("TRY","").replace(",","."))/float(order[22].replace("TRY","").replace(",",".")),
                sapNumber=order[8]
            )
            hodm.save()

            hodm.setTotalPrice()

            hom.setTotalPrice()
            hom.setPriceToBilling()

            hom.setCustomer(customer, customerData)
            hom.setCargo(order[2])

    def getHepsiOrders(self):
        orders = self.getHepsiOrdersAPI()

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
                    orderNumber=order.get("orderNumber"),
                    orderDate=date,
                    orderStatus=order.get("status")
                )
                hom.save()
                hom.setUserMarket("hepsiburada")

                details = self.getDetails(hom.orderNumber)

                for detail in details:
                    hodm = HepsiOrderDetailModel(
                        mom=hom,
                        priceToBilling=detail.get("priceToBilling"),
                        totalHbDiscount=detail.get("totalHbDiscount"),
                        mpm=hepsiProducts.get(marketplaceSku=detail.get("sku")),
                        quantity=detail.get("quantity"),
                        commissionRate=detail.get("commissionRate")*1.18,
                        sapNumber=detail.get("sapNumber")
                    )
                    hodm.save()
                    hodm.dropStock()

                    hodm.setTotalPrice()

                hom.setTotalPrice()
                hom.setPriceToBilling()
            else:
                hom = hom.first()
            
            hom.setCustomer(customer, customerData)
            hom.setCargo(order["cargoCompany"])


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
