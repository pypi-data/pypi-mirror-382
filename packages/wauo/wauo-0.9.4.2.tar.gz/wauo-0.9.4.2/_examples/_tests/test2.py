from wauo import WauoSpider

spider = WauoSpider()
url = "https://www.baidu.com"
resp = spider.go(url)
print(len(resp.text))
print(resp.text[:66])
