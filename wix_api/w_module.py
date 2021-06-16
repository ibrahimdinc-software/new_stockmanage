from .models import WixAuthTokensModel, WixProductModel, WixProductUpdateModel
from .w_api import WixAuthAPI, WixInventoryAPI, WixProductAPI

from datetime import datetime, timedelta


class WixAuthModule(WixAuthAPI):
    def requestAccessToken(self, code):
        res = self.getAccessToken("authorization_code", code)

        if res.get("success") == False:
            return False

        o, c = WixAuthTokensModel.objects.get_or_create(refreshToken=res.get("refresh_token"))
        o.authToken = res.get("access_token")
        o.save()

        return True
    
    def renewAccessToken(self, code):
        res = self.getAccessToken("refresh_token", code)

        o, c = WixAuthTokensModel.objects.get_or_create(refreshToken=res.get("refresh_token"))
        o.authToken = res.get("access_token")
        o.time = datetime.now()
        o.save()


    def getToken(self):
        tokenModel = WixAuthTokensModel.objects.all().first()
        if datetime.now() - tokenModel.time >= timedelta(minutes=4):
            self.renewAccessToken(code=tokenModel.refreshToken)
        
        return tokenModel.authToken



class WixProductModule(WixProductAPI, WixInventoryAPI):
    def createUpdateModel(self, product, quantity):
        wpum = WixProductUpdateModel.objects.filter(updated=False)
        if wpum:
            wpum = wpum.first()
            wpum.quantity += quantity
        else:
            wpum = WixProductUpdateModel(
                product=product,
                quantity=quantity
            )
        wpum.save()

    def addWixProductDetail(self, mpm, detail):
        wpm = WixProductModel(marketproductmodel_ptr_id=mpm.id)
        wpm.__dict__.update(mpm.__dict__)
        wpm.variantId = detail.get("variantId")
        wpm.save()

    def getWixProducts(self):
        token = WixAuthModule().getToken()
        products = self.getProductsAPI(token)
        productList = []

        for p in products:
            detail = self.getWixProuctVariantAPI(p.get("id"), token)
            for d in detail:
                #! variant sku veya product sku boşsa hata mesajı döndür
                #! varyantlı ürünler
                data = {
                    "marketType": "wix",
                    "productName": p.get("name"),
                    "marketplaceSku": p.get("id"),
                    "sellerSku": d["variant"].get("sku"),
                    "variantId": d.get("id"),
                    "salePrice": float(p["priceData"]["price"]),
                    "onSale": p["stock"]["inStock"],
                    "availableStock": p["stock"]["quantity"],
                    "productLink": p["productPageUrl"]["base"][:-1]+p["productPageUrl"]["path"]
                }
                productList.append(data)

        return productList
    
    def getWixProductDetails(self):
        detail = self.getWixProductDetailAPI(id, WixAuthModule().getToken())
        return detail

        
    def updateWixProduct(self, product):
        
        product = WixProductModel.objects.get(pk=product.pk)
        token = WixAuthModule().getToken()

        detail = self.getWixProductDetailAPI(product.marketplaceSku, token)

        data = {}

        res = False

        changeQuantity = product.availableStock - detail.get("stock").get("quantity")

        if changeQuantity > 0: 
            data["incrementData"] = [
                {
                    "productId": product.marketplaceSku,
                    "variantId": product.variantId,
                    "incrementBy": changeQuantity
                }
            ]
            res = self.wixIncrementAPI(token, data)
        else:
            data["decrementData"] = [
                {
                    "productId": product.marketplaceSku,
                    "variantId": product.variantId,
                    "decrementBy": abs(changeQuantity)
                }
            ]
            res = self.wixDecrementAPI(token, data)
                    
        return res





