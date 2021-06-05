from datetime import date, datetime, timedelta
from nonbir_api.n_module import NOrderModule, NProductModule
from nonbir_api.models import NProductModel
import time

from trendyol_api.models import TrendProductModel, TrendOrderModel
from trendyol_api.tr_module import TrendProductModule, TrendOrderModule

from hepsiburada_api.models import HepsiProductModel, HepsiOrderModel
from hepsiburada_api.hb_module import HepsiProductModule, HepsiOrderModule

from .models import MarketOrderModel, MarketProductBuyBoxListModel, MarketProductModel, MarketUpdateQueueModel


class ExtraMethods():
    def marketType(self, mpm):
        if mpm.userMarket.marketType == "trendyol":
            return TrendProductModel
        elif mpm.userMarket.marketType == "hepsiburada":
            return HepsiProductModel
        elif mpm.userMarket.marketType == "n11":
            return NProductModel

    def cleanBbModel(self, bbList):
        for bb in bbList:
            bb.delete()

    def renewBbModel(self, bbList, mpm):
        bbs = mpm.marketproductbuyboxlistmodel_set.all()
        for bb in bbList:
            if bbs.filter(merchantName=bb.get("merchantName")):
                b = bbs.get(merchantName=bb.get("merchantName"))

                b.uncomp = True if b.uncomp and b.price == bb.get("price") else False # rekabet edilemez ve fiyat değişmediyse True

                b.rank = bb.get("rank")
                b.oldPrice = b.price
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
                    oldPrice=0,
                    dispatchTime=bb.get("dispatchTime") if bb.get("dispatchTime") else None
                )


                mpbbl.save()
                bbs = bbs.exclude(merchantName=bb.get("merchantName"))

            if bb.get("merchantName") == "PetiFest":
                mpm.buyBoxRank = bb.get("rank")
                mpm.save()
        self.cleanBbModel(bbs)


class ProductModule(HepsiProductModule, TrendProductModule, NProductModule, ExtraMethods):
    def getProducts(self):
        productList = []
        productList += self.getHepsiProducts()
        productList += self.getTrendProducts()
        productList += self.getNProducts()

        mpms = MarketProductModel.objects.all()
        for p in productList:
            marketProduct = mpms.filter(marketplaceSku=p.get("marketplaceSku")).first()
            if not marketProduct:
                marketProduct = MarketProductModel(
                    productName=p.get("productName"),
                    marketplaceSku=p.get("marketplaceSku"),
                    availableStock=p.get("availableStock"),
                    onSale=p.get("onSale"),
                    sellerSku=p.get("sellerSku"),
                    salePrice=p.get("salePrice"),
                    productLink=p.get("productLink")
                )
            else:
                marketProduct.productName = p.get("productName")
                marketProduct.onSale = p.get("onSale")
                marketProduct.sellerSku = p.get("sellerSku")
                marketProduct.salePrice = p.get("salePrice")
                marketProduct.productLink = p.get("productLink")
                
            marketProduct.save()
            marketProduct.setUserMarket(p.get("marketType"))

            self.addProductDetails(marketProduct, p)

    def addProductDetails(self, mpm, details):
        if details.get("marketType") == "trendyol":
            tpm = TrendProductModel(
                marketproductmodel_ptr_id=mpm.id)
            tpm.__dict__.update(mpm.__dict__)

            tpm.listPrice = details.get("listPrice")

            tpm.save()
        elif details.get("marketType") == "hepsiburada":
            hpm = HepsiProductModel(
                marketproductmodel_ptr_id=mpm.id)
            hpm.__dict__.update(mpm.__dict__)
            hpm.DispatchTime = details.get("DispatchTime")
            hpm.CargoCompany1 = details.get("CargoCompany1")
            hpm.CargoCompany2 = details.get("CargoCompany2")
            hpm.CargoCompany3 = details.get("CargoCompany3")

            hpm.save()
        elif details.get("marketType") == "n11":
            self.addNProductDetails(mpm, details)

    def updateProducts(self):
        muqs = MarketUpdateQueueModel.objects.filter(isUpdated=False)
        if muqs:
            hpmList = []
            tpmList = []
            npmList = []
            for muq in muqs:
                if self.marketType(muq.mpm) == HepsiProductModel:
                    hpmList.append(muq.mpm)
                elif self.marketType(muq.mpm) == TrendProductModel:
                    tpmList.append(muq.mpm)
                elif self.marketType(muq.mpm) == NProductModel:
                    npmList.append(muq.mpm)
                muq.isUpdated = True
                muq.save()

            self.updateHepsiProducts(hpmList)
            self.updateTrendProducts(tpmList)
            self.updateNProducts(npmList)

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

            self.renewBbModel(bbList, mpm)

            time.sleep(.100)
           
                
            if notif:
                
                bbtm = mpm.marketbuyboxtracemodel_set.first() 
                
                if bbtm and bbtm.isActive:
                   
                    rivals = mpm.marketproductbuyboxlistmodel_set.all().order_by("rank")

                    seller = rivals.filter(merchantName="PetiFest").first()

                    rivals = rivals.exclude(merchantName="PetiFest")

                    campaign = True if seller and seller.price != mpm.salePrice else False

                    if int(mpm.buyBoxRank) == 1:
                        change = True if rivals[0].price != rivals[0].oldPrice else False
                        if campaign and change:
                            return self._buyBoxMessage(lastRank, mpm, detail="Kampanya var fiyat önerilmiyor.")

                        elif change:
                            return self._buyBoxMessage(lastRank, mpm, detail="LOG2 \Buybox kazanılıyor. \nDaha kârlı fiyat {}₺ olabilir.".format(round(rivals[0].price-bbtm.priceStep, 2)))
                        
                        else:
                            return {"status": "same"}

                    elif len(rivals) < 1:
                        return self._buyBoxMessage(lastRank, mpm, detail="LOG1 \nRakip yok. \nBuybox kazandıran fiyat {}₺ olabilir.".format(round(bbtm.maxPrice, 2)))
                    
                    else:
                        change = False
                        for bb in rivals:
                            change = True if bb.price != bb.oldPrice or change else False

                            if bb.price - bbtm.priceStep >= bbtm.minPrice and not bb.uncomp :

                                price = mpm.salePrice if mpm.salePrice <= bb.price and mpm.salePrice - bbtm.priceStep >= bbtm.minPrice else bb.price

                                if int(mpm.buyBoxRank) > int(bb.rank) and change:  

                                    if mpm.salePrice < bb.price and mpm.salePrice - bbtm.priceStep < bbtm.minPrice:
                                        bb.uncomp=True
                                        bb.save()
                                        change = True

                                    elif price - bbtm.priceStep >= bbtm.minPrice:
                                        return self._buyBoxMessage(lastRank, mpm, detail="LOG3 Buybox kazandıran fiyat {}₺ olabilir.".format(price - bbtm.priceStep))  

                                elif int(mpm.buyBoxRank) == 1:
                                    return {"status": "same"}

                                elif int(mpm.buyBoxRank) < int(bb.rank) and change:
                                    return self._buyBoxMessage(lastRank, mpm, detail="LOG4 Buybox kazandıran fiyat {}₺ olabilir.".format(bb.price - bbtm.priceStep))
                            
                            elif bb.price - bbtm.priceStep < bbtm.minPrice:
                                bb.uncomp = True
                                bb.save()
                                change = True if change else False
                        
                        return {"status": "same"}
                
                elif int(lastRank) != int(mpm.buyBoxRank):
                    return self._buyBoxMessage(lastRank, mpm, detail="Sıralamada değişiklik oldu.")
                
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

        mpms = MarketProductModel.objects.filter(onSale=True, lastControlDate__lte=tenMinAgo).exclude(userMarket__marketType="n11")[:20]

        infos = []

        for mpm in mpms:
            m = self._getBuyBox(mpm, True)
            if m.get("status") == "change":
                infos.append(m)
            
            mpm.lastControlDate = now
            mpm.save()

        if len(infos) > 0:
            return infos
            
        return []
    
    def cronBuyBoxTest(self, mpm):
        now = datetime.now()
        tenMinAgo = datetime.now()-timedelta(minutes=10)
        infos = []
        mpm.lastControlDate = now
        mpm.save()
        m = self._getBuyBox(mpm, True)
        if m.get("status") == "change":
            infos.append(m)
        if len(infos) > 0:
            return infos
        return []


class OrderModule(HepsiOrderModule, TrendOrderModule, NOrderModule):
    def getOrders(self):
        self.getTrendOrders()
        self.getHepsiOrders()
        self.getNOrders()

    def getOldOrders(self, date):
        self.getOldTrendOrders(date)

    def getDeliveredOrders(self):
        self.getDeliveredTrendOrders()
