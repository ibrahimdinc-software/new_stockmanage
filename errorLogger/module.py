from .models import ErrorLoggingModel
from new_stockmanage.mail import sendMail


def createErrorLoggingModel(errorType, errorLocation, errorMessage):
    elm = ErrorLoggingModel(
        errorType=errorType,
        errorLocation=errorLocation,
        errorMessage=errorMessage
    )
    elm.save()

    sendMail("Yeni Hata Var!", 'Hatanın detayları:{url}'.format(url=elm.get_admin_url()))





