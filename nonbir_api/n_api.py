import requests

import xmltodict
from xml.etree import ElementTree as et

from errorLogger.module import createErrorLoggingModel


baseUrl = "https://api.n11.com/ws/"

auth = {
    "appKey": "5322eec2-6516-47a3-9d3a-46649f3e889b",
    "appSecret": "DcJqBm164HGO6ndU"
}

headers = {
    'Content-Type': 'text/xml'
}

baseContent = {
    "soapenv:Envelope": {
        "@xmlns:soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
        "@xmlns:sch": "http://www.n11.com/ws/schemas",

        "soapenv:Header": {},
        "soapenv:Body": None
    }

}


class ShipmentApi:
    additionUrl = "ShipmentService.wsdl"
    def getShipmentTemplateAPI(self):
        b = baseContent
        b["soapenv:Envelope"]["soapenv:Body"] = {
            "sch:GetShipmentTemplateListRequest": {
                "auth": auth,
            }
        }
        response = requests.post(
            baseUrl+self.additionUrl,
            data=xmltodict.unparse(b),
            headers=headers
        ).content

        res = xmltodict.parse(response)["SOAP-ENV:Envelope"]["SOAP-ENV:Body"]["ns3:GetShipmentTemplateListResponse"]
        x = res["shipmentTemplates"]["shipmentTemplate"]

        

        if res["result"]["status"] == "success":
            shipmentTemplateList = []
            if type(x) == list:
                for i in x:
                    shipmentTemplateList.append(i.get("templateName"))
            else:
                shipmentTemplateList.append(x.get("templateName"))

            return shipmentTemplateList
        else:
            createErrorLoggingModel(
                errorType="N11 Entegrasyonu",
                errorLocation="nonbir_api/n_api.py:64",
                errorMessage=res["result"]["errorCode"] + "\n" + res["result"]["errorMessage"]
            )
            return "ERROR"


class NProductAPI:
    def getWPageN(self, page):
        baseContent["soapenv:Envelope"]["soapenv:Body"] = {
            "sch:GetProductListRequest": {
                "auth": auth,
                "pagingData": {
                    "currentPage": page,
                    "pagesize": 100
                }
            }
        }
        response = requests.post(
            baseUrl+"ProductService.wsdl",
            data=xmltodict.unparse(baseContent),
            headers=headers
        ).content

        res = xmltodict.parse(
            response
        )["SOAP-ENV:Envelope"]["SOAP-ENV:Body"]["ns3:GetProductListResponse"]

        if res["result"]["status"] == "success":
            return res
            
        createErrorLoggingModel(
            errorType="N11 Entegrasyonu",
            errorLocation="nonbir_api/n_api.py:92",
            errorMessage=res["result"]["errorCode"] + "\n" + res["result"]["errorMessage"]
        )

    def getNProductAPI(self):
        n_res = []

        page = 0
        totalPages = 2
        while totalPages != page:
            result = self.getWPageN(page)

            page += 1
            totalPages = int(result["pagingData"]["pageCount"])
            result = result["products"]["product"]
            if type(result) == list:
                [n_res.append(r) for r in result]
            else:
                n_res.append(result)
        return n_res 

    def getPdetail(self, sku):
        baseContent["soapenv:Envelope"]["soapenv:Body"] = {
            "sch:GetProductBySellerCodeRequest": {
                "auth": auth,
                "sellerCode": sku
            }
        }

        response = requests.post(
            baseUrl+"ProductService.wsdl",
            data=xmltodict.unparse(baseContent).encode("utf-8"),
            headers=headers
        ).content

        res = xmltodict.parse(
            response
        )["SOAP-ENV:Envelope"]["SOAP-ENV:Body"]["ns3:GetProductBySellerCodeResponse"]

        if res["result"]["status"] == "success":
            return res
        else:
            createErrorLoggingModel(
                errorType="N11 Entegrasyonu",
                errorLocation="nonbir_api/n_api.py:136",
                errorMessage=res["result"]["errorCode"] + "\n" + res["result"]["errorMessage"]
            )
            return "ERROR"

    def updateNProductAPI(self, product):
        baseContent["soapenv:Envelope"]["soapenv:Body"] = {
            "sch:SaveProductRequest": {
                "auth": auth,
                "product": product
            }
        }

        response = requests.post(
            baseUrl+"ProductService.wsdl",
            data=xmltodict.unparse(baseContent).encode("utf-8"),
            headers=headers
        ).content

        res = xmltodict.parse(
            response
        )["SOAP-ENV:Envelope"]["SOAP-ENV:Body"]["ns3:SaveProductResponse"]

        if res["result"]["status"] == "failure":
            createErrorLoggingModel(
                errorType="N11 Entegrasyonu",
                errorLocation="nonbir_api/n_api.py:166",
                errorMessage=res["result"]["errorCode"] + "\n" + res["result"]["errorMessage"]
            )
        return res



class NOrderAPI:
    def getWPageN(self, page, status=None, startDate=None, endDate=None):
        baseContent["soapenv:Envelope"]["soapenv:Body"] = {
            "sch:OrderListRequest": {
                "auth": auth,
                "searchData":{
                    "status": status if status else "",
                    "period": {
                        "startDate": startDate if startDate else "",
                        "endDate": endDate if endDate else "",
                    },
                },
                "pagingData": {
                    "currentPage": page,
                    "pagesize": 100
                }
            }
        }
        response = requests.post(
            baseUrl+"OrderService.wsdl",
            data=xmltodict.unparse(baseContent),
            headers=headers

        ).content
        
        res = xmltodict.parse(
            response
        )["SOAP-ENV:Envelope"]["SOAP-ENV:Body"]

        if res["ns3:OrderListResponse"]:
            res = res["ns3:OrderListResponse"]
        else:
            return None

        if res["result"]["status"] == "success":
            return res
        
        createErrorLoggingModel(
            errorType="N11 Entegrasyonu",
            errorLocation="nonbir_api/n_api.py:204",
            errorMessage=res["result"]["errorCode"] + "\n" + res["result"]["errorMessage"]
        )
        return None

    def getNOrderAPI(self, status=None, startDate=None, endDate=None):
        n_res = []

        page = 0
        totalPages = 2
        while page < totalPages:
            result = self.getWPageN(
                page,
                status if status else None,
                startDate if startDate else None,
                endDate if endDate else None,
            )
            

            if result == None or result["orderList"] == None:
                return n_res 

            page += 1
            totalPages = int(result["pagingData"]["pageCount"])
            result = result["orderList"]["order"]
            if type(result) == list:
                [n_res.append(r) for r in result]
            else:
                n_res.append(result)

        return n_res 

    def getNOrderDetailAPI(self, orderNId):
        baseContent["soapenv:Envelope"]["soapenv:Body"] = {
            "sch:OrderDetailRequest": {
                "auth": auth,
                "orderRequest":{
                    "id": str(orderNId)
                }
            }
        }
        response = requests.post(
            baseUrl+"OrderService.wsdl",
            data=xmltodict.unparse(baseContent),
            headers=headers
        ).content

        res = xmltodict.parse(
            response
        )["SOAP-ENV:Envelope"]["SOAP-ENV:Body"]["ns3:OrderDetailResponse"]

        if res["result"]["status"] == "success":
            return res

        
        createErrorLoggingModel(
            errorType="N11 Entegrasyonu",
            errorLocation="nonbir_api/n_api.py:262",
            errorMessage=res["result"]["errorCode"] + "\n" + res["result"]["errorMessage"]
        )

        return [] #!
