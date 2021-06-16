from wix_api.w_module import WixAuthModule
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
# Create your views here.


def installWix(request):
    installUrl = "https://www.wix.com/installer/install?appId=54954e33-345e-4eef-af36-1fe998a7a9e3&redirectUrl={}&token={}".format(
        "https://dev.petifest.com/wix-auth",
        request.GET.get("token") if request.GET.get("token") else ""
    )
    return HttpResponseRedirect(installUrl)


def authWix(request):
    tokens = WixAuthModule().requestAccessToken(code=request.GET.get("code"))

    if tokens.get("success") == False:
        redirect(installWix)

    return HttpResponseRedirect("https://www.wix.com/installer/token-received?access_token={}".format(tokens.get("access_token")))

    