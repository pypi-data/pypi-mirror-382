import requests

anti_content = "0asAfx5e-wCEXSzWXVxV6v11Yy8VVnq0YClO73O9pGomwxFMuTtenYMlXkL9mwbq6BTiT_gmetjOa8O3Z0H6V05tmm2jHicEtU0HloDaEa5HXi25nc9m3SLCPa6TfBpPXEpS2zJlO4L5H0R2pgA9xUHlI6k7b9E5b4LKMk2jwx-7uSsnW2-siZmgLaohN2IpH9hr9EqMCXeerH2ZSRYioA9jwx-Qum0uoxVjSmCx5lCKv8idtMGoz0cxjUWidGuXLdQkOveBlX7ZtgPEMvX9GGN1Ab3zmVFFfTdssoKLRW-shOvelkFFlE0Uv3qWI3RwM3htUn1_bkrTaQ129bQl_X5XjX5PjnGgqXpdJn5TYnuTJX5gqnG_aXGTyXGOb9BVbZYt3whfve-vVEqvApr3FuF3hTULKoIB_VSV9XnYZNovo9Gdp9yy0lavC9t-fFEtj_E-zCIl2Ed3t_BKqe3e3DS-xIDLx-DtzVbAbpbRhCS3Bw-KqIbKqeM38OIlBmd9w8UD8VSHBm9CCH2Zz-fweFTGTykgTzhs5UBPeg32mLwgTEV_wgVNdBAzksKzwsBAA-B2DbvDOseNprxoVjgIjaCdATdbAWU6hCkzs-wFeXu3V6SMspS-B3HhbHxbpDBZAdKAmS7B99kMl72eZw0A91"

headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5",
    "Anti-Content": anti_content,
    "cache-control": "no-cache",
    "content-type": "application/json",
    "origin": "https://pifa.pinduoduo.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://pifa.pinduoduo.com/search?word=%E8%82%9D%E8%83%86%E5%8F%8C%E6%B8%85%E9%A2%97%E7%B2%92&met=manual&refer_page_id=66237_1724125638579_c6aae04a9",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/538.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0"
}

url = "https://pifa.pinduoduo.com/pifa/search/queryGoods"
payload = {
    "page": 4,
    "size": 20,
    "sort": 0,
    "query": "肝胆双清颗粒",
    "propertyItems": [],
}
response = requests.post(url, headers=headers, json=payload)

print(response.text)
print(response)
