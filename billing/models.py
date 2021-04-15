from django.db import models

# Create your models here.

class CustomerModel(models.Model):
    name = models.CharField(verbose_name="İsim", max_length=255)
    taxId = models.CharField(verbose_name="TC No / Vergi No", max_length=255, blank=True, null=True)
    mail = models.CharField(verbose_name="E-Posta", max_length=255, blank=True, null=True)
    phone = models.CharField(verbose_name="Telefon", max_length=255, blank=True, null=True)
    province = models.CharField(verbose_name="İl", max_length=255, blank=True, null=True)
    district = models.CharField(verbose_name="İlçe", max_length=255, blank=True, null=True)
    address = models.CharField(verbose_name="Adres Bilgisi", max_length=500, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.taxId:
            self.taxId = "11111111111"
        super(CustomerModel, self).save(*args, **kwargs)

    def __str__(self):
        return self.name