import requests
import base64
import json

supplierId = "230796"
apiKey = "TkgLO3JguKqXJUjk7Kmh"
apiSecret = "eSLkr1XC7Jf9fASQf2zm"


def encode():
    up_encode = apiKey+":"+apiSecret
    up_encode = up_encode.encode("utf-8")
    b64_encode = base64.b64encode(up_encode)
    return "Basic " + str(b64_encode, 'utf-8')

class Product:
    headers = {
        "Authorization": encode()
    }
    url = "https://api.trendyol.com/sapigw/suppliers/"+supplierId+"/products"

    def batchControl(self, controlId):
        response = requests.get(self.url+"/batch-requests/"+controlId, headers=self.headers)
        result = response.content.decode("utf-8")
        print(result)
        return json.loads(result)

    def get(self):
        
        response = requests.get(self.url+"?size=500", headers=self.headers)

        if not response.status_code == 200:
            return
        result = json.loads(response.content.decode("utf-8"))["content"]

        return result

    def update(self,p_list):
        data = {
            "items":p_list
        }
        print(json.dumps(data))
        response = requests.post(self.url+"/price-and-inventory", json=data, headers=self.headers)
        result = json.loads(response.content)
        print(result, "\n TR_API.PY \n LINE:44")
        return result.get("batchRequestId")



class Order:
    url = "https://api.trendyol.com/sapigw/suppliers/"+supplierId+"/orders"
    headers = {
        "Authorization": encode()
    }
    def getWPage(self,page):
        response = requests.get(
            self.url+"?status=Awaiting,Created,Picking&page="+str(page), 
            headers=self.headers
        )
        return json.loads(response.content)


    def get(self):
        result = self.getWPage(0)
        
        n_res = []

        page = 0
        totalPages = 2
        while totalPages != page :
            result = self.getWPage(page)
            n_res += result.get("content")

            page += 1
            totalPages = result.get("totalPages")

        return n_res