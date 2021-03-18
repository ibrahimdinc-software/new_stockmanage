from django.core.checks import messages
from django.core.mail import send_mail

def sendMail(subject, message):
    send_mail(subject,message,'ibrahimdinc1999@gmail.com',['ibrahimdinc1999@gmail.com'])


def outOfStockMail(cdm):
    sendMail(
        'Stok Bitti', 
        cdm.baseProduct.name + ' ürününün ' + str(cdm.buyDate) + ' alım tarihli stoğu bitti! \n Acilen güncelleme yapılmalı.'
        )

def testMail():
    sendMail('Test', 'test mesaj')

def loseBuyboxMail(data):
    message = ""
    for m in data:
        message += "{} stok kodlu ürünün buybox sıralaması {}'den {}'ye düşmüştür\n. {}\n".format(m.get("tpm"), m.get("lastRank"), m.get("currentRank"), m.get("url"))

    sendMail(
        "BuyBox Kaybedildi!!!",
        message
    )
