import requests
import base64

import xmltodict
import json

from xml.etree import ElementTree as et

base_url = "https://mpop.hepsiburada.com/"

dev_user = "PetiFest_Dev"
dev_pass = "!IasvVxJkMXIzu"

merchant_id = "6555aefb-86d4-4fd8-bd85-232cbd8f23ab"



def encode():
    up_encode = dev_user+":"+dev_pass
    up_encode = up_encode.encode("utf-8")
    b64_encode = base64.b64encode(up_encode)
    return "Basic " + str(b64_encode, 'utf-8')

def authenticate(request=None):
    request = {
        "username": dev_user,
        "password": dev_pass,
        "authenticationType": "INTEGRATOR"    
    }
    return requests.post(base_url+"api/authenticate", json=request)

def xmldict(xml):
    return xmltodict.parse(xml)


class Listing:
    listing_url = "https://listing-external.hepsiburada.com/listings/merchantid/"
    
    hepiHeaders = {
        "Authorization": encode(),
        'Content-Type': 'application/xml'
    }

    def getHepsiProductAPI(self):
        a = requests.get(self.listing_url+merchant_id, headers=self.hepiHeaders).content
        
        result = xmldict(a)
        result = result["Result"]["Listings"]["Listing"]
        return result

    def update(self,product):
        listings = et.Element('listings')    
        if type(product) == list:
            for p in product:
                listing = et.SubElement(listings, 'listing')
                for k,v in p.items():
                    e = et.SubElement(listing, k)
                    e.text = str(v)
                    del e    
        else:
            listing = et.SubElement(listings, 'listing')
            for k,v in product.items():
                e = et.SubElement(listing, k)
                e.text = str(v)
                del e


        data = et.tostring(listings)
        
        response = requests.post(self.listing_url+merchant_id+"/inventory-uploads", headers=self.hepiHeaders, data=data).content

        js = xmldict(response)
        
        return js.get("Result")

    def controlListing(self,id):
        response = requests.get(self.listing_url+merchant_id+"/inventory-uploads/id/"+id, headers=self.hepiHeaders).content
        js = xmldict(response)
        return js.get("Result")

    def getHepsiBuyboxList(self,hbSku):
        """
        Örnek Cevap
        <?xml version="1.0"?>
        <Result xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <Variants>
                <Variant>
                    <Sku>HBV00000NDL8B</Sku>
                    <BuyboxOrders>
                        <BuyboxOrder>
                            <Rank>4</Rank>
                            <MerchantName>Evinemama</MerchantName>
                            <Price>13.51</Price>
                            <DispatchTime>0</DispatchTime>
                            <MerchantRating xsi:nil="true" />
                        </BuyboxOrder>
                        <BuyboxOrder>
                            <Rank>5</Rank>
                            <MerchantName>Coco petshop</MerchantName>
                            <Price>15</Price>
                            <DispatchTime>0</DispatchTime>
                            <MerchantRating xsi:nil="true" />
                        </BuyboxOrder>
                        <BuyboxOrder>
                            <Rank>1</Rank>
                            <MerchantName>PativeMama</MerchantName>
                            <Price>11</Price>
                            <DispatchTime>0</DispatchTime>
                            <MerchantRating xsi:nil="true" />
                        </BuyboxOrder>
                        <BuyboxOrder>
                            <Rank>7</Rank>
                            <MerchantName>Petimister</MerchantName>
                            <Price>20.9</Price>
                            <DispatchTime>3</DispatchTime>
                            <MerchantRating xsi:nil="true" />
                        </BuyboxOrder>
                        <BuyboxOrder>
                            <Rank>6</Rank>
                            <MerchantName>Birtiklagelir</MerchantName>
                            <Price>20.02</Price>
                            <DispatchTime>1</DispatchTime>
                            <MerchantRating xsi:nil="true" />
                        </BuyboxOrder>
                        <BuyboxOrder>
                            <Rank>2</Rank>
                            <MerchantName>Meow Meow</MerchantName>
                            <Price>12</Price>
                            <DispatchTime>0</DispatchTime>
                            <MerchantRating xsi:nil="true" />
                        </BuyboxOrder>
                        <BuyboxOrder>
                            <Rank>3</Rank>
                            <MerchantName>özlempet</MerchantName>
                            <Price>12.5</Price>
                            <DispatchTime>0</DispatchTime>
                            <MerchantRating xsi:nil="true" />
                        </BuyboxOrder>
                        <BuyboxOrder>
                            <Rank>8</Rank>
                            <MerchantName>petihtiyaç</MerchantName>
                            <Price>23.76</Price>
                            <DispatchTime>0</DispatchTime>
                            <MerchantRating xsi:nil="true" />
                        </BuyboxOrder>
                    </BuyboxOrders>
                </Variant>
            </Variants>
        </Result>
        """
        url = "https://listing-external.hepsiburada.com/buybox-orders/merchantid/"+merchant_id+"?skuList="+str(hbSku)
        response = requests.get(url, headers=self.hepiHeaders)
        if response.status_code != 200:
            return None
        js = xmldict(response.content)

        data = js["Result"]["Variants"]["Variant"]
        data = data.get("BuyboxOrders").get("BuyboxOrder")

        if type(data) != list:
            return [data]
        return data


class HepsiOrderAPI:
    hepsiurl = "https://oms-external.hepsiburada.com/orders/merchantid/"
    hepsiHeaders = {
        "Authorization": encode(),
        'Content-Type': 'application/json'
    }
    
    def hepsiGet(self):
        req = requests.get(self.hepsiurl+merchant_id, headers=self.hepsiHeaders).content
        
        response = json.loads(req.decode('utf-8'))

        orders = []

        for order in response["items"]:
            o = {
                "name": order["customerName"],
                "orderNumber": order.get("orderNumber"),
                "orderId": order.get("orderId"),
                "orderDate": order.get("orderDate"),
                "totalPrice": order["totalPrice"]["amount"],
                "status": order["status"]
            }
            orders.append(o)

        return orders

    def getDetails(self,orderNumber):
        response = json.loads(
            requests.get(
                self.hepsiurl+merchant_id+"/ordernumber/"+orderNumber, 
                headers=self.hepsiHeaders
            ).content
        )

        details = []

        for detail in response.get("items"):
            d = {
                "sku": detail.get("sku"),
                "id": detail.get("id"),
                "priceToBilling": detail.get("totalPrice").get("amount"),
                "totalHbDiscount": detail.get("hbDiscount").get("totalPrice").get("amount"),
                "quantity": detail.get("quantity")
            }
            details.append(d)

        return details

    def getPackageDetails(self):
        response = json.loads(
            requests.get(
                "https://oms-external.hepsiburada.com/packages/merchantid/"+merchant_id+"?timespan=120",
                headers=self.headers
            ).content
        )
        data = []
        for r in response:
            d = {
                "customerName": r["recipientName"],
                "orderNumber": r["items"][0]["orderNumber"],
                "orderDate": r["orderDate"],
                "packageNumber": r["packageNumber"],
                "status": r["status"],
                "priceToBilling": r["totalPrice"]["amount"],
                "detail": []
            }
            for detail in r["items"]:
                det = {
                    "marketplaceSku":detail["hbSku"],
                    "totalHbDiscount": detail["totalHBDiscount"]["amount"],
                    "priceToBilling": detail["merchantTotalPrice"]["amount"],
                    "totalPrice": detail["totalPrice"]["amount"],
                    "quantity": detail["quantity"]
                }
                d["detail"].append(det)
            data.append(d)
            
        
        return data


class Accounting:
    url = "https://mpfinance-external.hepsiburada.com/invoices/merchantid/"
    headers = {
        "Authorization": encode(),
        'Content-Type': 'application/json'
    }

    def getWoffset(self, offset, endDate, startDate, tType):
        response = json.loads(
            requests.get(self.url+merchant_id+"/transactiontype/"+tType+"?offset="+str(offset)+"&endDate="+endDate+"&startDate="+startDate+"&useInvoiceDate=false",
                headers=self.headers).content
        )

        return response

    def get(self, tType, endDate, startDate):
        response = self.getWoffset(offset=0, endDate=endDate, startDate=startDate, tType=tType)

        count = response["count"]
        offset = 10
        limit = 10

        data = response["items"]
        while count > offset:
            response = self.getWoffset(offset=offset, endDate=endDate, startDate=startDate, tType=tType)
            data += response["items"]
            offset += limit

        return data











