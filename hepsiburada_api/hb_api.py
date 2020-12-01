import requests
import base64

import xmltodict
import json

from xml.etree import ElementTree as et

base_url = "https://mpop.hepsiburada.com/"

dev_user = "meowmeow_dev"
dev_pass = "!jqZKsyIKeIfHE"

merchant_id = "99222e7e-4470-45d2-82d4-5e1d6c67958d"



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
    
    headers = {
        "Authorization": encode(),
        'Content-Type': 'application/xml'
    }

    def get(self):
        a = requests.get(self.listing_url+merchant_id, headers=self.headers).content
        
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
        
        response = requests.post(self.listing_url+merchant_id+"/inventory-uploads", headers=self.headers, data=data).content

        js = xmldict(response)
        return js.get("Result")



    def controlListing(self,id):
        response = requests.get(self.listing_url+merchant_id+"/inventory-uploads/id/"+id, headers=self.headers).content
        js = xmldict(response)
        return js.get("Result")



class Order:
    url = "https://oms-external.hepsiburada.com/orders/merchantid/"
    headers = {
        "Authorization": encode(),
        'Content-Type': 'application/json'
    }
    def get(self):
        req = requests.get(self.url+merchant_id, headers=self.headers).content
        
        response = json.loads(req.decode('utf-8'))

        orders = []

        for order in response["items"]:
            o = {
                "name": order["shippingAddress"]["name"],
                "orderNumber": order.get("orderNumber"),
                "orderId": order.get("orderId"),
                "orderDate": order.get("orderDate"),
                "totalPrice": order["totalPrice"]["amount"]
            }
            orders.append(o)

        return orders

    def getDetails(self,orderNumber):
        response = json.loads(
            requests.get(
                self.url+merchant_id+"/ordernumber/"+orderNumber, 
                headers=self.headers
            ).content
        )

        details = []

        for detail in response.get("items"):
            d = {
                "sku": detail.get("sku"),
                "id": detail.get("id"),
                "totalPrice": detail.get("totalPrice").get("amount"),
                "quantity": detail.get("quantity")
            }
            details.append(d)

        return details
