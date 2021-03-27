import time

from trendyol_api.models import TrendProductModel, TrendOrderModel
from trendyol_api.tr_module import TrendProductModule, TrendOrderModule

from hepsiburada_api.models import HepsiProductModel, HepsiOrderModel
from hepsiburada_api.hb_module import HepsiProductModule, HepsiOrderModule

from .models import MarketProductBuyBoxListModel, MarketProductModel, MarketUpdateQueueModel


class ExtraMethods():
    def marketType(self, mpm):
        hpm = HepsiProductModel.objects.filter(marketplaceSku=mpm.marketplaceSku)
        if hpm:
            return HepsiProductModel, hpm.first()
        tpm = TrendProductModel.objects.filter(marketplaceSku=mpm.marketplaceSku)
        if tpm:
            return TrendProductModel, tpm.first()


    def cleanBbModel(self, mpm):
        for mpbblm in MarketProductBuyBoxListModel.objects.filter(mpm=mpm):
            mpbblm.delete()


class ProductModule(HepsiProductModule, TrendProductModule, ExtraMethods):
    def getProducts(self):
        self.getHepsiProducts()
        self.getTrendProducts()

    def updateProducts(self):
        muqs = MarketUpdateQueueModel.objects.filter(isUpdated=False)
        if muqs:
            hpmList = []
            tpmList = []
            for muq in muqs:
                p = muq.mpm
                if type(p) == HepsiProductModel:
                    hpmList.append(p)
                elif type(p) == TrendProductModel:
                    tpmList.append(p)
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

    def _hepsiBuyBoxSet(self, mpm, bbList):
        if bbList:
            for bb in bbList:
                MarketProductBuyBoxListModel(
                    mpm=mpm,
                    rank=bb.get("Rank"),
                    merchantName=bb.get("MerchantName"),
                    price=bb.get("Price"),
                    dispatchTime=bb.get("DispatchTime")
                ).save()

                if bb.get("MerchantName") == "PetiFest":
                    mpm.buyBoxRank = bb.get("Rank")
                    mpm.save()

    def _trendBuyBoxSet(self, mpm, bbList):
        if bbList:
            for bb in bbList:
                MarketProductBuyBoxListModel(
                    mpm=mpm,
                    rank=bb.get("rank"),
                    merchantName=bb.get("merchantName"),
                    price=bb.get("price"),
                ).save()
        
                if bb.get("merchantName") == "PetiFest":
                    mpm.buyBoxRank = bb.get("rank")
                    mpm.save()

    def _buyBoxMessage(self, lastRank, mpm):
        d =  {
                "status": "change",
                "lastRank": lastRank,
                "currentRank": mpm.buyBoxRank,
                "mpm": mpm.sellerSku
            }
        if self.marketType(mpm)[0] == HepsiProductModel:
            d["url"] = "http://dev.petifest.com/admin/hepsiburada_api/hepsiproductmodel/{}/change/".format(mpm.id)
            #!TO-DO
        return

    def _getBuyBox(self, mpm, notif):
        self.cleanBbModel(mpm)

        if mpm.onSale:
            lastRank = mpm.buyBoxRank

            marketType = self.marketType(mpm)

            if marketType[0] == HepsiProductModel:
                self._hepsiBuyBoxSet(mpm, self._getHepsiBuyBox(marketType[1]))

            elif marketType[0] == TrendProductModel:
                self._trendBuyBoxSet(mpm, self._getTrendBuyBox(marketType[1]))


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




