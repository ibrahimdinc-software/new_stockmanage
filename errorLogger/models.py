from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

# Create your models here.


class ErrorLoggingModel(models.Model):
    errorType = models.CharField(verbose_name="Hata Türü", max_length=100)
    errorLocation = models.CharField(verbose_name="Hata Konumu", max_length=100)
    errorMessage = models.TextField(verbose_name="Hata Mesajı", max_length=1000)
    date = models.DateTimeField(verbose_name="Tarih", auto_now_add=True)
    isReported = models.BooleanField(verbose_name="Bildirildi mi", default=False)

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))

