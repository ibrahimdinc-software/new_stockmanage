from datetime import datetime
from marketplace.models import MarketOrderDetailModel
from billing.models import CustomerModel
from .n_api import NOrderAPI, NProductAPI, ShipmentApi
from .models import NORDER_STATUS, NOrderModel, NProductDiscountModel, NProductModel, NProductImageModel


class ShipmentModule(ShipmentApi):
    def getShipmentTemplate(self):
        pass


class NProductModule(NProductAPI):

    def _addProductImages(self, npm, images):
        npim = npm.nproductimagemodel_set.all()

        if npim:
            for np in npim:
                np.delete()
        for pi in images if type(images) == list else [images]:
            pim = NProductImageModel(
                nProductModel=npm,
                imageUrl=pi["url"],
                order=pi["order"]
            )
            pim.save()

    def addNProductDetails(self, mpm, details):
        npm = NProductModel(marketproductmodel_ptr_id=mpm.id)
        npm.__dict__.update(mpm.__dict__)
        npm.displayPrice = details.get("displayPrice")
        npm.subtitle = details.get("subtitle")
        npm.description = details.get("description")
        npm.category = int(details.get("category"))
        npm.currencyType = details.get("currencyType")
        npm.productCondition = details.get("productCondition")
        npm.preparingDay = details.get("preparingDay")
        npm.shipmentTemplate = details.get("shipmentTemplate")
        npm.brand = details.get("brand")
        npm.n11CatalogId = details.get("n11CatalogId")
        npm.save()

        self._addProductImages(npm, details.get("images"))

        if details.get("discount"):
            for npd in npm.nproductdiscountmodel_set.all():
                npd.delete()
            npdm = NProductDiscountModel(
                npm = npm,
                type=details.get("discount")["type"],
                value=details.get("discount")["value"]
            )
            npdm.save()

    def getNProducts(self):
        products = self.getNProductAPI()
        productList = []

        for p in products:
            pDetail = self.getPdetail(p.get("productSellerCode"))["product"]
            data = {
                "marketType": "n11",
                "productName": p.get("title"),
                "marketplaceSku": p.get("id"),
                "sellerSku": p.get("productSellerCode"),
                "salePrice": float(p.get("price")),
                "onSale": True if p.get("saleStatus") == "2" else False,
                "availableStock": int(p["stockItems"]["stockItem"]["quantity"]),
                "productLink": "https://urun.n11.com/--P"+p.get("id"),

                "displayPrice": float(p.get("displayPrice")),
                "subtitle": p.get("subtitle"),
                "description": pDetail.get("description"),
                "category": pDetail["category"]["id"],
                "currencyType": p.get("currencyType"),
                "productCondition": pDetail.get("productCondition"),
                "preparingDay": pDetail.get("preparingDay"),
                "shipmentTemplate": pDetail.get("shipmentTemplate"),
                "images": [],
                "discount": pDetail["discount"] if pDetail.get("discount") else None,
                "n11CatalogId": None
            }
            pAttr = pDetail["attributes"]["attribute"]
            pImages = pDetail["images"]["image"]
            
            for b in pAttr if type(pAttr) == list else [pAttr] :
                if b["name"] == "Marka":
                    data["brand"] = b["value"]

            for pim in pImages if type(pImages) == list else [pImages] :
                data["images"].append({
                    "order": pim["order"],
                    "url": pim["url"]
                })
            
            if pDetail["stockItems"]["stockItem"].get("n11CatalogId"):
                data["n11CatalogId"] = pDetail["stockItems"]["stockItem"]["n11CatalogId"]

            productList.append(data)

        return productList

    def updateNProduct(self, npm):
        npm = NProductModel.objects.get(id=npm.id)
        item = {
            "productSellerCode": npm.sellerSku,
            "title": npm.productName,
            "subtitle": npm.subtitle,
            "description": npm.description,
            "category": {
                "id": str(npm.category),
            },
            "price": npm.salePrice,
            "currencyType": npm.currencyType,
            "productCondition": npm.productCondition,
            "preparingDay": npm.preparingDay,
            "shipmentTemplate": npm.shipmentTemplate,
            "stockItems": {
                "stockItem":{
                    "quantity": npm.availableStock,
                    "n11CatalogId": npm.n11CatalogId if npm.n11CatalogId else None,
                }
            },
            "attributes":{
                "attribute":{
                    "name": "Marka",
                    "value": npm.brand
                }
            },
            "images":{
                "image": []
            }
        }

        for pim in npm.nproductimagemodel_set.all():
            item["images"]["image"].append({
                "url": pim.imageUrl,
                "order": pim.order
            })

        npdm = npm.nproductdiscountmodel_set.all()
        
        if npdm:
            item["discount"] = {
                "type": npdm.first().type,
                "value": npdm.first().value 
            }

        result = self.updateNProductAPI(item)

        if result["result"]["status"] == "success":
            return True
        
        if result["result"]["errorCode"] == "IMPORT_PRODUCT.imageDownloadInvalidHttpStatusCode":
            pDetail = self.getPdetail(npm.sellerSku)
            self._addProductImages(npm, pDetail["images"]["image"])
            return self.updateNProduct(npm)

        return False



class NOrderModule(NOrderAPI):
    def getNOrders(self):
        orders = []
        orders += self.getNOrderAPI("New")
        orders += self.getNOrderAPI("Approved")
        orders += self.getNOrderAPI("Rejected")

        nOrders = NOrderModel.objects.all()
        nProducts = NProductModel.objects.all()

        for order in orders:
            orderDetail = self.getNOrderDetailAPI(order["id"])["orderDetail"]
            customer, customerData = CustomerModel.objects.get_or_create(name=orderDetail["billingAddress"]["fullName"])

            if not customerData:
                customerData = orderDetail["billingAddress"]
                customerData["province"] = customerData["city"]
                customerData["taxId"] = customerData.get("taxId") if customerData.get("taxId") else customerData["tcId"]
                customerData["mail"] = orderDetail["buyer"]["email"]
                customerData["phone"] = customerData["gsm"]
            
            nom = None
            if not nOrders.filter(orderNumber=order["orderNumber"]):
                nom = self.createNOrder(nProducts, orderDetail)
            else:
                nom = nOrders.filter(orderNumber=order["orderNumber"]).first()
                nom.orderStatus = NORDER_STATUS.get(order["status"])
            
            nom.save()
            nom.setCustomer(customer, customerData)
            #! iptal edildiyse durumu eklenecek


    def createNOrder(self, nProducts, order, dropStock=True):
        date = datetime.strptime(order["createDate"], "%d/%m/%Y %H:%M")

        nom = NOrderModel(
            orderNumber=order["orderNumber"],
            orderDate=date,
            totalPrice=float(order["billingTemplate"]["originalPrice"]),
            priceToBilling=float(order["billingTemplate"]["dueAmount"]),
            orderStatus=order["status"]
        )

        nom.save()
        nom.setUserMarket("n11")

        details = order["itemList"]["item"]
        

        for d in details if type(details) == list else [details]:
            nodm = MarketOrderDetailModel(
            mpm=nProducts.get(marketplaceSku=d["productId"]),
            totalPrice=float(d["dueAmount"]),
            mom=nom,
            quantity=int(d["quantity"])
            )

            nodm.save()
            if dropStock:
                nodm.dropStock()

        return nom