from cs_api.models import CicekProductModel
from .cs_api import CicekProductAPI






class CicekProductModule(CicekProductAPI):
    
    def getCicekProducts(self):
        products = self.getCicekProductsAPI()

        pList = []

        for p in products:
            print(p)
            pList.append({
                "marketType": "cicek",
                "productName": p.get("productName"),
                "marketplaceSku": p.get("productCode"),
                "listPrice": p.get("listPrice"),
                "availableStock": p.get("stockQuantity"),
                "onSale": p.get("isActive"),
                "sellerSku": p.get("mainProductCode"),
                "salePrice": p.get("salesPrice"),
                "productLink": p.get("link")
            })

        return pList

    def addCicekProductDetail(self, mpm, details):
        #! detayları getir
        cpm = CicekProductModel(marketproductmodel_ptr_id=mpm.id)
        cpm.__dict__.update(mpm.__dict__)

        cpm. listPrice = details.get("listPrice")

        cpm.save()

    
    def updateCicekProduct(self, mpm):
        #sadece stok ve fiyat günceller
        cpm = CicekProductModel.objects.get(id=mpm.id)

        data = {
            "items": [
                {
                    "stockCode": cpm.sellerSku,
                    "StockQuantity": cpm.availableStock,
                    "listPrice": cpm.listPrice,
                    "salesPrice": cpm.salePrice
                }
            ]
        }

        #!batch id kontrol et
        return self.updateCicekProductAPI(data)



