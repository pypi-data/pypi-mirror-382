from wauo import WauoSpider

client = WauoSpider()
api = "https://pifa.pinduoduo.com/pifa/search/queryGoods"
payload = {"page": 1, "size": 20, "sort": 0, "query": "MacBookPro", "propertyItems": []}
resp = client.send(api, data=payload)
print(resp.json())
