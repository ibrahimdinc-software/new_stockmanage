import requests
import base64
import json
import re
from bs4 import BeautifulSoup


supplierId = ""
apiKey = ""
apiSecret = ""


def encodeTrend():
    up_encode = apiKey+":"+apiSecret
    up_encode = up_encode.encode("utf-8")
    b64_encode = base64.b64encode(up_encode)
    return "Basic " + str(b64_encode, 'utf-8')


class TrendProductAPI:

    trendHeaders = {
        "Authorization": encodeTrend(),
        "User-Agent": supplierId + " - " + apiKey
    }
    url = "https://api.trendyol.com/sapigw/suppliers/"+supplierId+"/products"

    def batchControl(self, controlId):
        response = requests.get(
            self.url+"/batch-requests/"+controlId, headers=self.trendHeaders)
        result = response.content.decode("utf-8")
        print(json.loads(result))
        return json.loads(result)

    def getWPage(self, page):
        response = requests.get(
            self.url+"?page="+str(page), headers=self.trendHeaders)
        result = json.loads(response.content.decode("utf-8"))
        return result

    def getTrendProductAPI(self):
        n_res = []

        page = 0
        totalPages = 2

        while totalPages != page:
            result = self.getWPage(page)
            n_res += result.get("content")

            page += 1
            totalPages = result.get("totalPages")

        return n_res

    def trendUpdate(self, p_list):
        data = {
            "items": p_list
        }
        response = requests.post(
            self.url+"/price-and-inventory", json=data, headers=self.trendHeaders)
        result = json.loads(response.content)

        return result.get("batchRequestId")

    def getTrendBuyboxList(self, link):
        page = requests.get(link, headers={'Cache-Control': 'no-cache'})

        data = re.search(r'"product":.*},"htmlContent"', page.text).group()
        data = data.replace('"product":', '')
        data = data.replace(',"htmlContent"', '')
        data = json.loads(data)

        lastData = [
            {
                "rank": 1,
                "merchantName": data["merchant"]["name"],
                "price": data["price"]["discountedPrice"]["value"]
            }
        ]

        r = 2
        for i in data["otherMerchants"]:
            lastData.append({
                "rank": r,
                "merchantName": i["merchant"]["name"],
                "price": i["price"]["discountedPrice"]["value"]
            })
            r += 1

        return lastData


class TrendOrderAPI:
    trendurl = "https://api.trendyol.com/sapigw/suppliers/"+supplierId+"/orders"
    trendHeaders = {
        "Authorization": encodeTrend(),
        "User-Agent": supplierId + " - " + apiKey
    }

    def getWPage(self, url, page, status=None, date=None, endDate=None, orderNumber=None):
        queryStr = ""

        queries = {
            "status": "status="+status if status else "",
            "page": "page="+str(page) if page else "",
            "date": "startDate="+str(date) if date else "",
            "endDate": "endDate="+str(endDate) if endDate else "",
            "orderNumber": "orderNumber"+str(orderNumber) if orderNumber else ""
        }

        for k in queries:
            if "?" in queryStr and len(queries[k]) > 0:
                queryStr += "&"+queries[k]
            elif len(queries[k]) > 0:
                queryStr += "?"+queries[k]

        url = url+queryStr
        response = requests.get(
            url,
            headers=self.trendHeaders
        )
        return json.loads(response.content)

    def get(self, status=None, date=None, endDate=None, orderNumber=None):
        n_res = []

        page = 0
        totalPages = 2
        while page < totalPages:
            result = self.getWPage(
                self.trendurl,
                page,
                status if status else None,
                date if date else None,
                endDate if endDate else None,
                orderNumber if orderNumber else None
            )
            n_res += result.get("content")

            page += 1
            totalPages = result.get("totalPages")
        return n_res
    