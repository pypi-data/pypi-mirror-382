from wauo import WauoSpider, SelectorResponse

session = WauoSpider(default_headers={"Cookie": "Your Cookies"})
url = "https://www.baidu.com"
resp: SelectorResponse = session.send(url)

print(resp)
print(resp.request.headers["Cookie"])  # 输出：Your Cookies

title = resp.get_one("//title/text()")
print(title)  # 输出：百度一下，你就知道
