import requests
import base64
import json
from bs4 import BeautifulSoup


supplierId = "356587"
apiKey = "YFZDBDCCxRRy1YBkwrrL"
apiSecret = "iaNnyoGaqnJEi0g3Pw9b"


def encode():
    up_encode = apiKey+":"+apiSecret
    up_encode = up_encode.encode("utf-8")
    b64_encode = base64.b64encode(up_encode)
    return "Basic " + str(b64_encode, 'utf-8')


class Product:
    headers = {
        "Authorization": encode(),
        "User-Agent": "356587 - YFZDBDCCxRRy1YBkwrrL"
    }
    url = "https://api.trendyol.com/sapigw/suppliers/"+supplierId+"/products"

    def batchControl(self, controlId):
        response = requests.get(
            self.url+"/batch-requests/"+controlId, headers=self.headers)
        result = response.content.decode("utf-8")
        print(result)
        return json.loads(result)

    def getWPage(self, page):
        response = requests.get(
            self.url+"?page="+str(page), headers=self.headers)
        result = json.loads(response.content.decode("utf-8"))
        return result

    def get(self):
        n_res = []

        page = 0
        totalPages = 2

        while totalPages != page:
            result = self.getWPage(page)
            n_res += result.get("content")

            page += 1
            totalPages = result.get("totalPages")

        return n_res

    def update(self, p_list):
        data = {
            "items": p_list
        }
        response = requests.post(
            self.url+"/price-and-inventory", json=data, headers=self.headers)
        result = json.loads(response.content)

        return result.get("batchRequestId")



    def getBuyboxList(self, link):
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')

        lastData = [
                {
                    "rank": 1,
                    "merchantName":soup.find("div", attrs={"class":"sl-nm"}).find("a").text,
                    "price": float(soup.find("span", attrs={"class":"prc-slg"}).text.replace(" TL", "").replace(",", "."))
                }
            ]

        r = 2
        for i in soup.find_all("div", attrs={"class":"pr-mc-w gnr-cnt-br"}):
            lastData.append({
                    "rank": r,
                    "merchantName": i.find("div",attrs={"class": "pr-mb-mn"}).find("a").text,
                    "price": float(i.find("span",attrs={"class": "prc-slg"}).text.replace(" TL", "").replace(",", "."))
                })
            r += 1


        return lastData


class Order:
    url = "https://api.trendyol.com/sapigw/suppliers/"+supplierId+"/orders"
    headers = {
        "Authorization": encode(),
        "User-Agent": "230796 - TkgLO3JguKqXJUjk7Kmh"
    }

    def getWPage(self, page, status):
        response = requests.get(
            self.url+"?status="+status+"&page="+str(page),
            headers=self.headers
        )
        print(response.content)
        return json.loads(response.content)

    def get(self, status):
        n_res = []

        page = 0
        totalPages = 2
        while page < totalPages:
            result = self.getWPage(page, status)
            n_res += result.get("content")

            page += 1
            totalPages = result.get("totalPages")

        return n_res
