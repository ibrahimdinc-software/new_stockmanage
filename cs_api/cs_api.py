import requests
import json

from errorLogger.module import createErrorLoggingModel


baseUrl = "https://apis.ciceksepeti.com/api/v1/"

headers = {
    "x-api-key": ""
}

class CicekProductAPI:
    
    def getCicekProductsAPI(self):
        url = baseUrl + "Products"

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            createErrorLoggingModel(
                errorType="Çiçek Sepeti Entegrasyon",
                errorLocation="cs_api/cs_api.py:21",
                errorMessage=str(response.status_code)
            )
            return []

        res = json.loads(response.content)
        return res["products"]
        
    def updateCicekProductAPI(self, data):
        url = baseUrl + "Products/price-and-stock"

        response = requests.put(url, headers=headers, json=data)
        if response.status_code != 200:
            createErrorLoggingModel(
                errorType="Çiçek Sepeti Entegrasyon",
                errorLocation="cs_api/cs_api.py:39",
                errorMessage=str(response.status_code)
            )
            return False
        #! batch id döndür
        return True

    def batchControlAPI(self, batchId):
        url = baseUrl + "Products/batch-status/" + batchId

        response = requests.get(url)

        if response.status_code != 200:
            createErrorLoggingModel(
                errorType="Çiçek Sepeti Entegrasyon",
                errorLocation="cs_api/cs_api.py:53",
                errorMessage=str(response.status_code)
            )
            return False
        



