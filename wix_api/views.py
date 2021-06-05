from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render

# Create your views here.


def installWix(request):
    installUrl = "https://www.wix.com/installer/install?appId=54954e33-345e-4eef-af36-1fe998a7a9e3&redirectUrl={}&token={}".format(
        "https://dev.petifest.com/wix-auth",
        request.GET.get("token") if request.GET.get("token") else ""
    )
    return HttpResponseRedirect(installUrl)


def authWix(request):
    content = """
        code: {} <br>
        state: {} <br>
        instanceId: {}
    """.format(
        request.GET.get("code"),
        request.GET.get("state"),
        request.GET.get("instanceId")
    )
    return HttpResponse(content)

    