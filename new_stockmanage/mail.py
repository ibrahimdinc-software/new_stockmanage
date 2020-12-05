from django.core.mail import send_mail

def sendMail(subject, message):
    send_mail(subject,message,'ibrahimdinc1999@gmail.com',['ibrahimdinc1999@gmail.com'])


def outOfStockMail(cdm):
    sendMail(
        'Stok Bitti', 
        cdm.baseProduct + ' ürününün ' + cdm.buyDate + ' alım tarihli stoğu bitti! \n Acilen güncelleme yapılmalı.'
        )

def testMail():
    sendMail('Test', 'test mesaj')

