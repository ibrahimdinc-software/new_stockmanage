from datetime import date, datetime
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

    def cleanBbModel(self, mpm):
        for mpbblm in MarketProductBuyBoxListModel.objects.filter(mpm=mpm):
            mpbblm.delete()


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
                marketProduct.marketType = p.get("marketType"),
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

   
    def _buyBoxMessage(self, lastRank, mpm):
        d = {
            "status": "change",
            "lastRank": lastRank,
            "currentRank": mpm.buyBoxRank,
            "mpm": mpm.sellerSku,
            "url": "http://dev.petifest.com/admin/marketplace/marketproductmodel/{}/change/".format(mpm.id)
        }
        return d

    def _getBuyBox(self, mpm, notif):
        self.cleanBbModel(mpm)

        if mpm.onSale:
            lastRank = mpm.buyBoxRank

            bbList = []

            if self.marketType(mpm) == HepsiProductModel:
                bbList += self._getHepsiBuyBox(mpm)
            elif self.marketType(mpm) == TrendProductModel:
                bbList += self._getTrendBuyBox(mpm)

            if bbList:
                for bb in bbList:
                    MarketProductBuyBoxListModel(
                        mpm=mpm,
                        rank=bb.get("rank"),
                        merchantName=bb.get("merchantName"),
                        price=bb.get("price"),
                        dispatchTime=bb.get("dispatchTime") if bb.get("dispatchTime") else None
                    ).save()

                    if bb.get("merchantName") == "PetiFest":
                        mpm.buyBoxRank = bb.get("rank")
                        mpm.save()

            if notif:
                if str(lastRank) != str(mpm.buyBoxRank):
                    return self._buyBoxMessage(lastRank, mpm)
                else:
                    return {
                        "status": "same"
                    }
            else:
                time.sleep(.100)
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
            messages += self._getBuyBox(mpm, False)
            messages += "\n"
        return messages

    def cronBuyBox(self):
        mpms = MarketProductModel.objects.filter(onSale=True)
        infos = []
        for mpm in mpms:
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
