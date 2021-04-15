from django.db import models

# Create your models here.

class CurrentModel(models.Model):
    name = models.CharField(verbose_name="İsim", max_length=255)
    no = models.CharField(verbose_name="TC No / Vergi No", max_length=255, blank=True, null=True)
    mail = models.CharField(verbose_name="E-Posta", max_length=255, blank=True, null=True)
    phone = models.CharField(verbose_name="Telefon", max_length=255, blank=True, null=True)
    address = models.CharField(verbose_name="Adres Bilgisi", max_length=500, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.no:
            self.no = "11111111111"
        super(CurrentModel, self).save(*args, **kwargs) # Call the real save() method
