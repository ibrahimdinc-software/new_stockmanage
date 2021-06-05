from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from .w_api import requestAccessToken
from .models import WixAuthTokensModel
# Create your views here.


def installWix(request):
    installUrl = "https://www.wix.com/installer/install?appId=54954e33-345e-4eef-af36-1fe998a7a9e3&redirectUrl={}&token={}".format(
        "https://dev.petifest.com/wix-auth",
        request.GET.get("token") if request.GET.get("token") else ""
    )
    return HttpResponseRedirect(installUrl)


def authWix(request):
    tokens = requestAccessToken("authorization_code", request.GET.get("code"))

    if tokens.get("success") == False:
        redirect(installWix)

    o, c = WixAuthTokensModel.objects.get_or_create(refreshToken=tokens.get("refresh_token"))
    if not c:
        o.authToken = tokens.get("access_token")
        o.save()

    return HttpResponseRedirect("https://www.wix.com/installer/token-received?access_token={}".format(tokens.get("access_token")))

    