from datetime import date, datetime, timedelta
import time

from trendyol_api.models import TrendProductModel, TrendOrderModel
from trendyol_api.tr_module import TrendProductModule, TrendOrderModule

from hepsiburada_api.models import HepsiProductModel, HepsiOrderModel
from hepsiburada_api.hb_module import HepsiProductModule, HepsiOrderModule

from .models import MarketOrderModel, MarketProductBuyBoxListModel, MarketProductModel, MarketUpdateQueueModel


class ExtraMethods():
    def marketType(self, mpm):
        if mpm.marketType == "trendyol":
            return TrendProductModel
        elif mpm.marketType == "hepsiburada":
            return HepsiProductModel        

    def cleanBbModel(self, bbList):
        for bb in bbList:
            bb.delete()

    def renewBbModel(self, bbList, mpm):
        bbs = mpm.marketproductbuyboxlistmodel_set.all()
        change = False
        for bb in bbList:
            if bbs.filter(merchantName=bb.get("merchantName")):
                b = bbs.get(merchantName=bb.get("merchantName"))

                change = True if b.price != bb.get("price") or b.rank != bb.get("rank") else False

                b.uncomp = True if b.uncomp and b.price == bb.get("price") else False # rekabet edilemez ve fiyat değişmediyse True

                b.rank = bb.get("rank")
                b.price = bb.get("price")
                b.dispatchTime = bb.get("dispatchTime") if bb.get("dispatchTime") else None
                b.save()
                bbs = bbs.exclude(merchantName=bb.get("merchantName"))

            else:
                mpbbl = MarketProductBuyBoxListModel(
                    mpm=mpm,
                    rank=bb.get("rank"),
                    merchantName=bb.get("merchantName"),
                    price=bb.get("price"),
                    dispatchTime=bb.get("dispatchTime") if bb.get("dispatchTime") else None
                )

                change = True

                mpbbl.save()
                bbs = bbs.exclude(merchantName=bb.get("merchantName"))

            if bb.get("merchantName") == "PetiFest":
                mpm.buyBoxRank = bb.get("rank")
                mpm.save()
        self.cleanBbModel(bbs)

        return change

class ProductModule(HepsiProductModule, TrendProductModule, ExtraMethods):
    def getProducts(self):
        productList = []
        productList += self.getHepsiProducts()
        productList += self.getTrendProducts()

        mpms = MarketProductModel.objects.all()
        for p in productList:
            marketProduct = mpms.filter(marketplaceSku=p.get("marketplaceSku")).first()
            if not marketProduct:
                marketProduct = MarketProductModel(
                    marketType=p.get("marketType"),
                    productName=p.get("productName"),
                    marketplaceSku=p.get("marketplaceSku"),
                    availableStock=p.get("availableStock"),
                    onSale=p.get("onSale"),
                    sellerSku=p.get("sellerSku"),
                    salePrice=p.get("salePrice"),
                    productLink=p.get("productLink")
                )
            else:
                marketProduct.marketType = p.get("marketType")
                marketProduct.productName = p.get("productName")
                marketProduct.onSale = p.get("onSale")
                marketProduct.sellerSku = p.get("sellerSku")
                marketProduct.salePrice = p.get("salePrice")
                marketProduct.productLink = p.get("productLink")
                
            marketProduct.save()

            if p.get("marketType") == "trendyol":
                tpm = TrendProductModel(
                    marketproductmodel_ptr_id=marketProduct.id)
                tpm.__dict__.update(marketProduct.__dict__)

                tpm.listPrice = p.get("listPrice")

                tpm.save()
            elif p.get("marketType") == "hepsiburada":
                hpm = HepsiProductModel(
                    marketproductmodel_ptr_id=marketProduct.id)
                hpm.__dict__.update(marketProduct.__dict__)
                hpm.DispatchTime = p.get("DispatchTime")
                hpm.CargoCompany1 = p.get("CargoCompany1")
                hpm.CargoCompany2 = p.get("CargoCompany2")
                hpm.CargoCompany3 = p.get("CargoCompany3")

                hpm.save()

    def updateProducts(self):
        muqs = MarketUpdateQueueModel.objects.filter(isUpdated=False)
        if muqs:
            hpmList = []
            tpmList = []
            for muq in muqs:
                if muq.mpm.marketType == "hepsiburada":
                    hpmList.append(muq.mpm)
                elif muq.mpm.marketType == "trendyol":
                    tpmList.append(muq.mpm)
                muq.isUpdated = True
                muq.save()

            self.updateHepsiProducts(hpmList)
            self.updateTrendProducts(tpmList)

    def updateQueue(self, qs):
        marketUpdateQueueModels = MarketUpdateQueueModel.objects.all()
        if not 'count' in dir(qs):
            if not marketUpdateQueueModels.filter(mpm=qs, isUpdated=False):
                muq = MarketUpdateQueueModel(mpm=qs)
                muq.save()
        elif qs.count() > 1:
            for p in qs:
                if not marketUpdateQueueModels.filter(mpm=p, isUpdated=False):
                    muq = MarketUpdateQueueModel(mpm=p)
                    muq.save()
        else:
            if not marketUpdateQueueModels.filter(mpm=qs[0], isUpdated=False):
                muq = MarketUpdateQueueModel(mpm=qs[0])
                muq.save()

    def dropStock(self, product, quantity):
        marketMedProductModels = product.marketmedproductmodel_set.all()
        for marketMedProductModel in marketMedProductModels:
            medProductModels = marketMedProductModel.product.medproductmodel_set.all()
            for medProductModel in medProductModels:
                medProductModel.base_product.dropStock(
                    quantity*medProductModel.piece)

    def increaseStock(self, product, quantity):
        marketMedProductModels = product.marketmedproductmodel_set.all()
        for marketMedProductModel in marketMedProductModels:
            medProductModels = marketMedProductModel.product.medproductmodel_set.all()
            for medProductModel in medProductModels:
                medProductModel.base_product.increaseStock(
                    quantity*medProductModel.piece)

   
    def _buyBoxMessage(self, lastRank, mpm, detail):
        d = {
            "status": "change",
            "lastRank": lastRank,
            "currentRank": mpm.buyBoxRank,
            "mpm": mpm.sellerSku,
            "url": "http://dev.petifest.com/admin/marketplace/marketproductmodel/{}/change/".format(mpm.id),
            "detail": detail
        }
        return d

    def _getBuyBox(self, mpm, notif):
        if mpm.onSale:
            lastRank = mpm.buyBoxRank

            bbList = []

            if self.marketType(mpm) == HepsiProductModel:
                bbList += self._getHepsiBuyBox(mpm)
            elif self.marketType(mpm) == TrendProductModel:
                bbList += self._getTrendBuyBox(mpm)

            change = None

            if bbList:
                change = self.renewBbModel(bbList, mpm)

            time.sleep(.100)
           
                
            if notif:
                bbtm = mpm.marketbuyboxtracemodel_set.first()
                if bbtm and change:
                    rivals = mpm.marketproductbuyboxlistmodel_set.all()
                    if len(rivals) < 1: #rakip yok
                        return self._buyBoxMessage(lastRank, mpm, detail="LOG1 \nRakip yok. \nBuybox kazandıran fiyat {}₺ olabilir.".format(round(bbtm.maxPrice, 2)))
                    
                    else:
                        
                        for bb in rivals:
                            
                            if bb.price - bbtm.priceStep >= bbtm.minPrice and not bb.uncomp:
                                # Rakibin fiyatı min fiyattan yüksekse ve rekabet edilebilirse
                                
                                price = mpm.salePrice if mpm.salePrice <= bb.price and mpm.salePrice - bbtm.priceStep >= bbtm.minPrice else bb.price
                                
                                if mpm.buyBoxRank > bb.rank: 
                                    # bizim sıralama rakipten büyükse

                                    if mpm.salePrice < bb.price and mpm.salePrice - bbtm.priceStep < bbtm.minPrice:
                                        bb.uncomp=True
                                        bb.save()
                                    
                                    elif price - bbtm.priceStep >= bbtm.minPrice:
                                        return self._buyBoxMessage(lastRank, mpm, detail="LOG3 Buybox kazandıran fiyat {}₺ olabilir.".format(price - bbtm.priceStep))  

                                    #elif bb.price - bbtm.priceStep >= mpm.salePrice:
                                    #    return self._buyBoxMessage(lastRank, mpm, detail="LOG4 Buybox kazandıran fiyat {}₺ olabilir.".format(bb.price - bbtm.priceStep))  
                                    
                                elif mpm.buyBoxRank == 1:
                                    return {"status": "same"}
                                        
                                elif mpm.buyBoxRank < bb.rank:
                                    return self._buyBoxMessage(lastRank, mpm, detail="LOG5 Buybox kazandıran fiyat {}₺ olabilir.".format(bb.price - bbtm.priceStep))
                            
                            elif bb.price - bbtm.priceStep < bbtm.minPrice:
                                bb.uncomp = True
                                bb.save()
                        
                        return self._buyBoxMessage(lastRank, mpm, detail="LOG6 Durumlar harici bir olay Buybox kazandıran fiyat {}₺ olabilir.".format(price - bbtm.priceStep))
                
                elif lastRank != mpm.buyBoxRank or change:
                    return self._buyBoxMessage(lastRank, mpm, detail="Sıralamada veya fiyatlarda değişiklik oldu.")
                
                else:
                    return {"status": "same"}
            
            else:
                return "{} -- Başarılı".format(mpm.sellerSku)
            
        elif notif:
            return {
                "status": "change",
                "lastRank": "-",
                "currentRank": "-",
                "tpm": mpm.sellerSku,
                "url": "HATALI"
            }
        else:
            return "{} -- Hata var!".format(mpm.sellerSku)


    def buyboxList(self, mpms):
        messages = ""
        for mpm in mpms:
            message = self._getBuyBox(mpm, False)
            if type(message) == dict:
                messages += str(message.get("tpm")) + " " + str(message.get("detail"))
            else:
                messages += message
            messages += "\n"
        return messages

    def cronBuyBox(self):
        now = datetime.now()
        tenMinAgo = datetime.now()-timedelta(minutes=10)
        mpms = MarketProductModel.objects.filter(onSale=True, lastControlDate__lte=tenMinAgo)[:20]
        infos = []
        for mpm in mpms:
            mpm.lastControlDate = now
            mpm.save()
            m = self._getBuyBox(mpm, True)
            if m.get("status") == "change":
                infos.append(m)
        if len(infos) > 0:
            return infos
        return []


class OrderModule(HepsiOrderModule, TrendOrderModule):
    def getOrders(self):
        self.getTrendOrders()
        self.getHepsiOrders()

    def getOldOrders(self, date):
        self.getOldTrendOrders(date)

    def getDeliveredOrders(self):
        self.getDeliveredTrendOrders()
