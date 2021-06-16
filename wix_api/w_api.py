from django.http import response
from errorLogger.module import createErrorLoggingModel
import requests, json

from requests.api import head

client_id = "54954e33-345e-4eef-af36-1fe998a7a9e3"
client_secret = "c650239b-38fc-4460-8bb7-ffa97562280f"


def _getHeaders(token):
    return {
        "Authorization": token
    }

class WixAuthAPI:
    def getAccessToken(self, grantType, code):
        data = {
            "grant_type": grantType,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        if grantType == "authorization_code":
            data["code"] = code
            
        elif grantType == "refresh_token":
            data["refresh_token"] = code

        response = requests.post(
            "https://www.wix.com/oauth/access",
            json=data
        ).content
        response = json.loads(response)
        return response
"""
class WixInventoryAPI:

    def getInventoryVariantsAPI(self, token, ):

"""

class WixInventoryAPI:

    wixInventoryUrl = "https://www.wixapis.com/stores/v2/inventoryItems/"
    def wixDecrementAPI(self, token, data):
        url = self.wixInventoryUrl + "decrement"
        
        res = requests.post(url, headers=_getHeaders(token), json=data)
        response = json.loads(res.content)

        if res.status_code != 200:
            return False
        
        return True

    def wixIncrementAPI(self, token, data):
        url = self.wixInventoryUrl + "increment"
        
        res = requests.post(url, headers=_getHeaders(token), json=data)

        if res.status_code != 200:
            return False
        
        return True


class WixProductAPI:
    
    wixProductUrl="https://www.wixapis.com/stores/v1/products/"

    def getProductsAPI(self, token):
        url = self.wixProductUrl+"query"
        pList = []

        offset, limit, total = 0, 20, 99
        while offset <= total:
            body = {
                "query": {
                    "paging":{
                        "limit": limit,
                        "offset": offset
                    }
                },
                "includeVariants": True,
                "includeHiddenProducts": True
            }
            res = requests.post(url, headers=_getHeaders(token), json=body)
            response = json.loads(res.content)
            if res.status_code != 200:
                createErrorLoggingModel(
                    "Wix",
                    "wix_api/w_api.py:65",
                    str(res.status_code)
                )
                raise Exception("Wix "+str(res.status_code))

            offset += limit
            total = response.get("totalResults")

            pList += response.get("products")

        return pList
    
    def getWixProductDetailAPI(self, productId, token):
        url = self.wixProductUrl + productId

        res = requests.get(url, headers=_getHeaders(token))
        response = json.loads(res.content)
        
        if res.status_code != 200:
            createErrorLoggingModel(
                "Wix",
                "wix_api/w_api.py:86",
                str(res.status_code)
            )
            raise Exception("Wix "+str(res.status_code) + "\n" + response)
        
        return response["product"]

    def getWixProuctVariantAPI(self, productId, token):
        url = self.wixProductUrl + productId + "/variants/query"
        body = {}

        res = requests.post(url, headers=_getHeaders(token), json=body)
        response = json.loads(res.content)

        if res.status_code != 200:
            createErrorLoggingModel(
                "Wix",
                "wix_api/w_api.py:89",
                str(res.status_code) + response.get("sku")
            )
            return []
        return response["variants"]

    def updateWixProductAPI(self, token, data):
        url = self.wixProductUrl + data.get("id")
        data.pop("id", None)
        
        res = requests.patch(url, headers=_getHeaders(token), json=data)
        response = json.loads(res.content)
        print(response)
        if res.status_code != 200:
            createErrorLoggingModel(
                "Wix",
                "wix_api/w_api.py:81",
                str(res.status_code)
            )

            return False

        return True


