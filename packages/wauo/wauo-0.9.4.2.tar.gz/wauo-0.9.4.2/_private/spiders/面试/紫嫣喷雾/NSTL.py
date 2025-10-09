from scrapy.item import Item, Field

from wauo import WauoSpider


class DataItem(Item):
    title = Field()
    author = Field()
    jg = Field()
    uni = Field()
    zy = Field()
    xw = Field()
    fyjg = Field()
    ds = Field()
    yz = Field()
    submit_date = Field()
    answer_date = Field()
    cate_id = Field()
    keywords = Field()
    desc = Field()


maps = {
    "tit": "title",
    "off": "jg",
    "uni": "uni",
    "maj": "zy",
    "deg": "xw",
    "lan": "yz",
    "lan": "submit_date",
    "lan": "answer_date",
    "clco": "cate_id",
    "key": "keywords",
    "abs": "desc",
}

api = "https://www.nstl.gov.cn/api/service/nstl/web/execute?target=nstl4.search4&function=paper/pc/list/pl"
payload = {
    "query": '{"c":10,"st":"0","f":[],"p":"","q":[{"k":"","v":"","e":1,"o":"AND","a":0},{"k":"yea","a":1,"o":"","f":1,"v":"2022"},{"k":"uni_s","a":1,"o":"","f":1,"v":"中国科学院大学"}],"op":"AND","s":["nstl","haveAbsAuK:desc","yea:desc","score"],"t":["DegreePaper"]}',
    "webDisplayId": "11",
    "sl": "1",
    "searchWordId": "5d6a31115d1a912a141764a262d4d053",
    "searchId": "3ab1cb83bbb878caed7845a37617e251",
    "facetRelation": '[{"id":"f6a3d55c514ca148cf53e240d1254c5e","sequence":3,"field":"yea","name":"年份","value":"2022"},{"id":"02013e509fa9475ebd96124147a53c22","sequence":1,"field":"uni_s","name":"院校","value":"中国科学院大学"}]',
    "pageSize": 30,
    "pageNumber": 1,
}
cli = WauoSpider()
res = cli.send(api, data=payload)
data = res.json()["data"]
print(len(data))


def findv(key: str, some: list):
    for one in some:
        if one["f"] == key:
            return one["v"]


for one in data:
    item = DataItem()
    for a in one:
        key, value = a["f"], a["v"]
        if src := maps.get(key):
            item[src] = value

        if key == "hasAut":
            author = findv("nam", value[0])
            item["author"] = author

        if key == "hasTut":
            teacher = findv("nam", value[0])
            item["ds"] = teacher

    # print(item["title"])
    # print(item["author"])
    # print(item["ds"])
    print(item)
    break
