import json
import requests

# get token
def get_token():
    body_token = json.dumps({
        "Query": {
            "Activate": {
                "RestAPI": "true",
                "WSAPI": "true"
            }
        }
    })
    header_token = {'appkey': 'CDP-App', 'cache-control': 'no-cache', 'Content-type': 'application/json',
                    'sensorcustomerkey': '500150', 'userkey': '500152', 'body': 'raw'}
    link = "https://cdp-dmz.cisco.com/extdeveng/fid-CIMUserInterface"
    try:

        data_token = requests.post(link, headers=header_token, data=body_token).json()

        return data_token['http']['token']
    except:
        return "can't connect!"


def get_wellness():
    token = get_token()
    body_wellness = json.dumps({
        "Query": {
            "Find": {
                "WasteBin": {
                    "as": "var.mybin",
                    "providerDetails": {
                        "provider": "wellness"
                    }
                },
                "UltrasonicSensor": {
                    "sid": {
                        "eq": "var.mybin.sensors.entityId"
                    }
                }
            }
        }
    }
    )

    header_wellness = {'appkey': 'CDP-App', 'cache-control': 'no-cache', 'Content-type': 'application/json',
                       'sensorcustomerkey': '500150', 'userkey': '500152', 'token': token, 'body': 'raw'}

    link = 'https://cdp-dmz.cisco.com/extdeveng/fid-CIMUserQueryInterface'
    data = requests.post(link, headers=header_wellness, data=body_wellness)
    data_wellness = data.json()
    return data_wellness


def get_sayme():
    token = get_token()
    body_sayme = json.dumps({
        "Query": {
            "Find": {
                "WasteBin": {
                    "as": "var.mybin",
                    "providerDetails": {
                        "provider": "sayme"
                    }
                },
                "UltrasonicSensor": {
                    "sid": {
                        "eq": "var.mybin.sensors.entityId"
                    }
                }
            }
        }
    }
    )

    header_sayme = {'appkey': 'CDP-App', 'cache-control': 'no-cache', 'Content-type': 'application/json',
                    'sensorcustomerkey': '500150', 'userkey': '500152', 'token': token, 'body': 'raw'}

    link = 'https://cdp-dmz.cisco.com/extdeveng/fid-CIMUserQueryInterface'
    data1 = requests.post(link, headers=header_sayme, data=body_sayme)
    data_sayme = data1.json()
    return data_sayme

#print(get_wellness())