from storage.models import ProductModel,BaseProductModel
from hepsiburada_api.models import HepsiProductModel, HepsiProductBuyBoxListModel
from trendyol_api.models import TrendProductModel



class ProductModule():
    def getUnassigned(self):
        unassigned = []
        bpms = BaseProductModel.objects.all()
        for bpm in bpms:
            mpm = bpm.medproductmodel_set.all()
            if len(mpm) == 0:
                unassigned.append(bpm)
        return unassigned

    def getUnassignedHB(self):
        unassigned = []
        hpms = HepsiProductModel.objects.all()
        for hpm in hpms:
            mpm = hpm.hepsimedproductmodel_set.all()
            if len(mpm) == 0:
                unassigned.append(hpm)
        return unassigned

    def getUnassignedTR(self):
        unassigned = []
        tpms = TrendProductModel.objects.all()
        for tpm in tpms:
            mpm = tpm.trendmedproductmodel_set.all()
            if len(mpm) == 0:
                unassigned.append(tpm)
        return unassigned

    def getLosedBuyboxesHB(self):
        losedBuybox = []

        hpms = HepsiProductModel.objects.all()

        for hpm in hpms:
            if hpm.buyBoxRank != 1:
                losedBuybox.append(hpm)

        

        return losedBuybox
















        