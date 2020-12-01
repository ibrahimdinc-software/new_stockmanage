from storage.models import ProductModel,BaseProductModel



class ProductModule():
    def getUnassigned(self):
        unassigned = []
        bpms = BaseProductModel.objects.all()
        for bpm in bpms:
            mpm = bpm.medproductmodel_set.all()
            if len(mpm) == 0:
                unassigned.append(bpm)
        return unassigned


















        