import requests, json

client_id = "54954e33-345e-4eef-af36-1fe998a7a9e3"
client_secret = "c650239b-38fc-4460-8bb7-ffa97562280f"



def requestAccessToken(grantType, code):
    data = None
    if grantType == "authorization_code":
        data = {
            "grant_type": grantType,
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code
        }
    elif grantType == "refresh_token":
        data = {
            "grant_type": grantType,
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": code
        }


    response = requests.post(
        "https://www.wix.com/oauth/access",
        json=data
    ).content
    response = json.loads(response)
    return response
