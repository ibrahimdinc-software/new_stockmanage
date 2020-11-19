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

    def getListing(self):
    
        headers = {
            "Authorization": encode()
            }
        
        a = requests.get(self.listing_url+merchant_id, headers=headers).content
        
        result = xmldict(a)
        result = result["Result"]["Listings"]["Listing"]

        return result


    def updateListing(self,product):
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

        headers = {
            "Authorization": encode(),
            'Content-Type': 'application/xml'
        }
        
        data = et.tostring(listings)
        
        response = requests.post(self.listing_url+merchant_id+"/inventory-uploads", headers=headers, data=data).content
        print(response)
        js = xmldict(response)
        print(js, 'HB_API.PY LINE:86')
        return js.get("Result")



    def controlListing(self,id):
        headers = {
            "Authorization": encode(),
            'Content-Type': 'application/xml'
        }
        response = requests.get(self.listing_url+merchant_id+"/inventory-uploads/id/"+id, headers=headers).content
        js = xmldict(response)
        return js.get("Result")


    def deleteProducts(self,products):
        for p in products:
            requests.delete(
                self.listing_url+merchant_id+"/sku/"+p.get("hbSku")+"/merchantSku/"+p.get("merchSku"),
                headers=self.headers
            )
         

class Order:
    url = "https://oms-external.hepsiburada.com/orders/merchantid/"
    def get_orders(self):
        headers = {
            "Authorization": encode(),
            'Content-Type': 'application/json'
        }

        req = requests.get(self.url+merchant_id, headers=headers).content
        
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

    def get_order_details(self,orderNumber):
        headers = {
            "Authorization": encode(),
            'Content-Type': 'application/json'
        }
        response = json.loads(
            requests.get(
                self.url+merchant_id+"/ordernumber/"+orderNumber, 
                headers=headers
            ).content
        )

        print(response)
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
