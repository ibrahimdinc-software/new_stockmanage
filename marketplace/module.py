from nonbir_api.n_api import ShipmentApi
from cs_api.cs_module import CicekProductModule
from cs_api.models import CicekProductModel
from datetime import datetime, timedelta
from wix_api.w_module import WixProductModule
from wix_api.models import WixProductModel
from nonbir_api.n_module import NOrderModule, NProductModule
from nonbir_api.models import NProductModel
import time

from trendyol_api.models import TrendProductModel
from trendyol_api.tr_module import TrendProductModule, TrendOrderModule

from hepsiburada_api.models import HepsiProductModel
from hepsiburada_api.hb_module import HepsiProductModule, HepsiOrderModule

from .models import COST_TYPES, MarketOrderPredCostModel, MarketProductBuyBoxListModel, MarketProductCommissionModel, MarketProductModel, MarketUpdateQueueModel, UserMarketShipmentRuleModel


class ExtraMethods():

    def marketType(self, mpm):
        if mpm.userMarket.marketType == "trendyol":
            return TrendProductModel
        elif mpm.userMarket.marketType == "hepsiburada":
            return HepsiProductModel
        elif mpm.userMarket.marketType == "n11":
            return NProductModel
        elif mpm.userMarket.marketType == "wix":
            return WixProductModel
        elif mpm.userMarket.marketType == "cicek":
            return CicekProductModel

    def cleanBbModel(self, bbList):
        for bb in bbList:
            bb.delete()

    def renewBbModel(self, bbList, mpm):
        bbs = mpm.marketproductbuyboxlistmodel_set.all()
        for bb in bbList:
            mName = bb.get("merchantName")[:-1] if bb.get("merchantName")[-1] == ' ' else bb.get("merchantName")
            b = bbs.filter(merchantName=mName).first()
            if b:
                b.isCompeted = True if b.isCompeted and b.price == float(bb.get("price")) else False  # rekabet edildi ve fiyat değişmediyse True
                b.rank = bb.get("rank")
                b.oldPrice = b.price
                b.price = bb.get("price")
                b.dispatchTime = bb.get("dispatchTime") if bb.get(
                    "dispatchTime") else None
                b.save()

            else:
                mpbbl = MarketProductBuyBoxListModel(
                    mpm=mpm,
                    rank=bb.get("rank"),
                    merchantName=mName,
                    price=bb.get("price"),
                    oldPrice=0,
                    dispatchTime=bb.get("dispatchTime") if bb.get(
                        "dispatchTime") else None
                )
                mpbbl.save()

            bbs = bbs.exclude(merchantName=mName)

            if bb.get("merchantName") == "PetiFest":
                mpm.buyBoxRank = bb.get("rank")
                mpm.save()
        self.cleanBbModel(bbs)


class ProductModule(
        HepsiProductModule,
        TrendProductModule,
        NProductModule,
        WixProductModule,
        CicekProductModule,
        ExtraMethods):

    def getProducts(self):
        mpms = MarketProductModel.objects.all()

        self._addProducts(mpms, self.getTrendProducts())
        self._addProducts(mpms, self.getHepsiProducts())
        #self._addProducts(mpms, self.getNProducts())
        #self._addProducts(mpms, self.getWixProducts())
        #self._addProducts(mpms, self.getCicekProducts())

    def _addProducts(self, mpms, productList):

        for p in productList:
            marketProduct = mpms.filter(
                marketplaceSku=p.get("marketplaceSku")).first()
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
            hpm.commissionRate = float(details.get("commissionRate")) * 1.18

            hpm.save()
        elif details.get("marketType") == "n11":
            self.addNProductDetails(mpm, details)
        elif details.get("marketType") == "wix":
            self.addWixProductDetail(mpm, details)
        elif details.get("marketType") == "cicek":
            self.addCicekProductDetail(mpm, details)

    def createCommissionModel(self, mpm, com):
        mpcm = MarketProductCommissionModel.objects.filter(mpm=mpm)
        #!
        mpcm = MarketProductCommissionModel(
            mpm=mpm,
            commissionRate=com
        )
        mpcm.save()

    def updateProducts(self):
        muqs = MarketUpdateQueueModel.objects.filter(isUpdated=False)
        if muqs:
            hpmList = []
            tpmList = []
            status = True
            for muq in muqs:
                if self.marketType(muq.mpm) == HepsiProductModel:
                    hpmList.append(muq.mpm)
                elif self.marketType(muq.mpm) == TrendProductModel:
                    tpmList.append(muq.mpm)
                elif self.marketType(muq.mpm) == NProductModel:
                    status = self.updateNProduct(muq.mpm)
                elif self.marketType(muq.mpm) == WixProductModel:
                    status = self.updateWixProduct(muq.mpm)
                elif self.marketType(muq.mpm) == CicekProductModel:
                    status = self.updateCicekProduct(muq.mpm)
                muq.isUpdated = status
                muq.save()

            self.updateHepsiProducts(hpmList)
            self.updateTrendProducts(tpmList)

    def directUpdateProduct(self, mpm):
        self.updateQueue(mpm)
        self.updateProducts()

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
            lastRank = mpm.buyBoxRank #ürün üzerinde görünen eski sıralama

            bbList = [] #pazaryerlerinden gelen buybox bilgelerinin tutulacağı yer

            if self.marketType(mpm) == HepsiProductModel:
                bbList += self._getHepsiBuyBox(mpm)
            elif self.marketType(mpm) == TrendProductModel:
                bbList += self._getTrendBuyBox(mpm)

            #rivals = mpm.marketproductbuyboxlistmodel_set.all().order_by("rank")

            self.renewBbModel(bbList, mpm)

            #rivals = mpm.marketproductbuyboxlistmodel_set.all().order_by("rank")

            time.sleep(.100)

            mpm.lastControlDate = datetime.now()
            mpm.save()

            if notif:

                bbtm = mpm.marketbuyboxtracemodel_set.first()

                if bbtm and bbtm.isActive:

                    rivals = mpm.marketproductbuyboxlistmodel_set.all().order_by("rank")

                    seller = rivals.filter(merchantName="PetiFest").first()

                    rivals = rivals.exclude(merchantName="PetiFest")
                    
                    discountRate = 1
                    campaign = True if seller.price != mpm.salePrice else False
                    if self.marketType(mpm) == HepsiProductModel:
                        campaign = False
                        discountRate = ((mpm.salePrice - seller.price) / mpm.salePrice)+1
                    if campaign:
                        return self._buyBoxMessage(lastRank, mpm, detail="Kampanya var fiyat önerilmiyor.")

                    target = 0
                    while target != len(rivals):
                        rival = rivals[target]
                        rPrice = rival.price * discountRate
                        if rPrice > bbtm.minPrice:  # rekabet edilebilir
                            # düşük fiyatı buluyoruz
                            price = rPrice if rPrice < mpm.salePrice or not rival.isCompeted else mpm.salePrice
                            # son fiyatı hesapladık
                            lPrice = round(price - bbtm.priceStep, 2)
                            if seller.rank == target + 1 and rival.isCompeted:
                                mpm.lastControlDate = datetime.now()
                                return self._buyBoxMessage(lastRank, mpm, detail="Hedefe ulaşıldı".format(lPrice))
                            if lPrice >= bbtm.minPrice and (lPrice < bbtm.maxPrice or not bbtm.recoMax):
                                mpm.salePrice = lPrice
                                mpm.lastControlDate = datetime.now()-timedelta(minutes=10)
                                mpm.save()
                                mpm.updateStock()

                                time.sleep(3)

                                rival.isCompeted = True
                                rival.save()
                                return self._buyBoxMessage(lastRank, mpm, detail="Buybox kazandıran fiyat {}₺ olabilir.".format(lPrice))

                        target += 1

                    if target == len(rivals):  # rekabet edilemedi
                        if bbtm.giveMax and seller.price != bbtm.maxPrice:
                            mpm.salePrice = bbtm.maxPrice
                            mpm.lastControlDate = datetime.now()-timedelta(minutes=10)
                            mpm.save()
                            mpm.updateStock()

                            time.sleep(3)

                            return self._buyBoxMessage(lastRank, mpm, detail="Buybox kazanılamıyor max fiyat {}₺ olabilir.".format(bbtm.maxPrice))
                        elif not bbtm.giveMax and seller.price != bbtm.minPrice:
                            mpm.salePrice = bbtm.minPrice
                            mpm.lastControlDate = datetime.now()-timedelta(minutes=10)
                            mpm.save()
                            mpm.updateStock()

                            time.sleep(3)

                            return self._buyBoxMessage(lastRank, mpm, detail="Buybox kazanılamıyor min fiyat {}₺ olabilir.".format(bbtm.minPrice))
                
                mpm.lastControlDate = datetime.now()
                return self._buyBoxMessage(lastRank, mpm, detail="???")

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
                messages += str(message.get("tpm")) + " " + \
                    str(message.get("detail"))
            else:
                messages += message
            messages += "\n"
        return messages

    def cronBuyBox(self):
        tenMinAgo = datetime.now()-timedelta(minutes=5)

        mpms = MarketProductModel.objects.filter(onSale=True,
                                                 lastControlDate__lte=tenMinAgo).exclude(userMarket__marketType__in=["n11", "wix", "cicek"])[:20]

        infos = []

        for mpm in mpms:
            m = self._getBuyBox(mpm, True)
            if m.get("status") == "change":
                infos.append(m)

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


class ProfitModule():
    def calcProfit(self, order):
        orderDetails = order.marketorderdetailmodel_set.all()
        orderCosts = order.marketorderpredcostmodel_set.all()
        shipmentRules = UserMarketShipmentRuleModel.objects.filter(
            userMarket=order.userMarket)

        if not orderCosts.filter(costType="shipment"):
            mopcm = self.createPredModel(order, None, "shipment")
            umsrm = shipmentRules.filter(minPrice__lte=order.priceToBilling,
                                         maxPrice__gte=order.priceToBilling, cargo__in=['tumu', order.cargo])
            print(umsrm)
            mopcm.costAmount = umsrm.first().cost
            mopcm.save()
        for od in orderDetails:
            if not orderCosts.filter(modm=od, costType="commission"):
                mopcm = self.createPredModel(order, od, "commission")
                mopcm.costAmount = od.getCommission()
                mopcm.save()
            #? neden gerekli
            elif orderCosts.filter(modm=od, costType="commission").first().costAmount == 0:
                mopcm = orderCosts.filter(
                    modm=od, costType="commission").first()
                mopcm.costAmount = od.getCommission()
                mopcm.save()
            #? son stoksa hata verir mi?
            if not orderCosts.filter(modm=od, costType="purchasePrice"):
                mopcm = self.createPredModel(order, od, "purchasePrice")
                mopcm.costAmount = od.mpm.getCost()
                mopcm.save()

    def createPredModel(self, mom, od, costType):
        mopcm = MarketOrderPredCostModel(
            mom=mom,
            modm=od,
            costType=costType
        )
        mopcm.save()
        return mopcm
