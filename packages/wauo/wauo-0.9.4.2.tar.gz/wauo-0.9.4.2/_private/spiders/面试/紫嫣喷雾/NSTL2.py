import random
import time

import pandas as pd
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
    URL = Field()


maps = {
    "tit": "title",
    "off": "jg",
    "uni": "uni",
    "maj": "zy",
    "deg": "xw",

    "lan": "yz",
    "suda": "submit_date",
    "quda": "answer_date",
    "clco": "cate_id",
    "key": "keywords",
    "abs": "desc",
}

cli = WauoSpider(is_session=False)


def get_dids():
    detail_ids = []
    api = "https://www.nstl.gov.cn/api/service/nstl/web/execute?target=nstl4.search4&function=paper/pc/list/pl"
    for i in range(2):
        payload = {
            "query": "{\"c\":10,\"st\":\"0\",\"f\":[],\"p\":\"\",\"q\":[{\"k\":\"\",\"v\":\"\",\"e\":1,\"o\":\"AND\",\"a\":0},{\"k\":\"yea\",\"a\":1,\"o\":\"\",\"f\":1,\"v\":\"2022\"},{\"k\":\"uni_s\",\"a\":1,\"o\":\"\",\"f\":1,\"v\":\"中国科学院大学\"}],\"op\":\"AND\",\"s\":[\"nstl\",\"haveAbsAuK:desc\",\"yea:desc\",\"score\"],\"t\":[\"DegreePaper\"]}",
            "webDisplayId": "11",
            "sl": "1",
            "searchWordId": "5d6a31115d1a912a141764a262d4d053",
            "searchId": "3ab1cb83bbb878caed7845a37617e251",
            "facetRelation": "[{\"id\":\"f6a3d55c514ca148cf53e240d1254c5e\",\"sequence\":3,\"field\":\"yea\",\"name\":\"年份\",\"value\":\"2022\"},{\"id\":\"02013e509fa9475ebd96124147a53c22\",\"sequence\":1,\"field\":\"uni_s\",\"name\":\"院校\",\"value\":\"中国科学院大学\"}]",
            "pageSize": 30,
            "pageNumber": i + 1
        }
        cli = WauoSpider()
        res = cli.send(api, data=payload)
        data = res.json()["data"]
        for one in data:
            for a in one:
                if a["f"] == "id":
                    detail_id = a["v"]
                    detail_ids.append(detail_id)
    return detail_ids


def findv(key: str, some: list):
    for one in some:
        if one["f"] == key:
            return one["v"]


detail_ids = get_dids()

items = []
for did in detail_ids:
    detail_api = "https://www.nstl.gov.cn/api/service/nstl/web/execute?target=nstl4.search4&function=paper/pc/detail"
    form = {
        "id": did,
        "webDisplayId": "1001",
        "searchWordId": "",
        "searchId": "",
        "searchSequence": ""
    }
    resp = cli.send(detail_api, data=form)
    time.sleep(random.uniform(1, 2))
    detail_url = "https://www.nstl.gov.cn/paper_detail.html?id={}".format(did)
    try:
        data = resp.json()["data"]
    except Exception as e:
        print(e)
        print(detail_url)
        continue
    item = DataItem()
    for a in data:
        key, value = a["f"], a["v"]
        if src := maps.get(key):
            item[src] = value
        if key == "hasAut":
            author = findv("nam", value[0])
            item["author"] = author
        if key == "hasTut":
            teacher = findv("nam", value[0])
            item["ds"] = teacher
    item['fyjg'] = item["uni"]
    item["URL"] = detail_url

    print(detail_url)
    for k, v in item.items():
        v0 = v[0]
        if isinstance(v0, str):
            if k in ["submit_date", "answer_date"]:
                item[k] = v0.split(" ")[0]
            else:
                item[k] = v0
        if isinstance(v0, dict):
            item[k] = list(v0.values())[0]

    items.append(item)

df = pd.DataFrame(items)
df.to_excel("中国科学院大学2.xlsx", index=False)
