import sys
import time
from threading import RLock

from wauo import WauoSpider
from wauo.utils import PoolMan

req = WauoSpider()
pool = PoolMan(speed=20)
n = 0
rlock = RLock()


def task(url, title):
    resp = req.send(url)
    rlock.acquire()
    global n
    n += 1
    rlock.release()
    print("第{}个\n{}\n{}\n{}\n".format(n, title, url, resp))


def main():
    def job(params: dict):
        resp = req.send(start_url, headers=headers, params=params)
        data = resp.json()
        for item in data["data"]["list"]:
            title = item["title"]
            link = item["url"]
            pool.add(task, link, title)

    username = "MarkAdc"
    start_url = "https://blog.csdn.net/community/home-api/v1/get-business-list"
    headers = {
        "Referer": "https://blog.csdn.net/" + username,
        "Cookie": "UN=MarkAdc; log_Id_pv=5291; log_Id_view=16967; log_Id_click=3757; Hm_up_6bcd52f51e9b3dce32bec4a3997715ac=%7B%22islogin%22%3A%7B%22value%22%3A%221%22%2C%22scope%22%3A1%7D%2C%22isonline%22%3A%7B%22value%22%3A%221%22%2C%22scope%22%3A1%7D%2C%22isvip%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%2C%22uid_%22%3A%7B%22value%22%3A%22MarkAdc%22%2C%22scope%22%3A1%7D%7D; Hm_ct_6bcd52f51e9b3dce32bec4a3997715ac=6525*1*10_28763253310-1624452950476-837833!5744*1*MarkAdc; _ga=GA1.2.1240831573.1704723950; _ga_7W1N0GEY1P=GS1.1.1706003969.3.0.1706003969.60.0.0; Hm_lvt_e5ef47b9f471504959267fd614d579cd=1709216701; fpv=7c5d6cab945c044d0be3f673fc40588e; cf_clearance=_BJaTU0iwsHw1v1kzVfopQWShXdQX0prxC.8GyjGxhg-1716469187-1.0.1.1-xSS3e9rNvoBoNVdskwvJDsyVBurzsqbNvin9nxo4ZZmdJXo5XZ.prWxI_aXdpuwrAWtjG3Ko6skSHhzxRs2ufg; UserName=MarkAdc; UserInfo=8bb8ac703a1747ea900a060b49339f84; UserToken=8bb8ac703a1747ea900a060b49339f84; UserNick=%E6%98%AF%E5%A4%A7%E5%98%9F%E5%98%9F%E5%91%80; AU=A02; BT=1718890582875; p_uid=U010000; Hm_lvt_ec8a58cd84a81850bcbd95ef89524721=1721649065; uuid_tt_dd=10_4541715570-1721914482699-408796; fid=20_61136309447-1723188973742-872573; csdn_newcert_MarkAdc=1; MarkAdccomment_new=1725238383974; FCNEC=%5B%5B%22AKsRol9OaoAszC965bLMzr3INPQQUbp0_-gP3F7lgqZCADuVdCOnr1ILsggFxspiHr2vlp-3ygIxj664qWiReaxW6iJzSRvb3HMUZXOY5Og1YQrfRL8YqJR1z9bqsyGkJrukXJFphecfA2tRZdV6jtCEoBZ4ohF14Q%3D%3D%22%5D%5D; c_segment=12; Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac=1729770943,1730189724,1730258212,1730809087; HMACCOUNT=BC30A28BCF335DB7; dc_sid=6c50fb2dad6f8d835c2b052278df76b3; c_dl_prid=1730725776120_194591; c_dl_rid=1730809226626_654949; c_dl_fref=https://blog.csdn.net/liberty888/article/details/131781577; c_dl_fpage=/download/weixin_38681646/13706883; c_dl_um=distribute.pc_search_result.none-task-blog-2%7Eblog%7Efirst_rank_ecpm_v1%7Erank_v31_ecpm-1-131781577-null-null.nonecase; https_waf_cookie=6b9b2562-86ce-4d2d53aac583c0beadd304dda6485d0b48ad; c_first_ref=www.bing.com; firstDie=1; __gads=ID=12d1a5f041a72479:T=1730386695:RT=1731936479:S=ALNI_MaVPcpKpo9qCk-rtZshi-WtdAKfzw; __gpi=UID=00000e306cef7c0e:T=1716825583:RT=1731936479:S=ALNI_Mb9wwfWgP7qLXwcpQvLY4EIvePjDg; __eoi=ID=b8add4e2db388962:T=1722874256:RT=1731936479:S=AA-AfjZAimS6wwiVVSfqGi3KAhO-; c_first_page=https%3A//blog.csdn.net/lianshaohua/article/details/109671105; c_pref=https%3A//www.bing.com/; c_ref=https%3A//blog.csdn.net/lianshaohua/article/details/109671105; creative_btn_mp=3; _clck=q9g315%7C2%7Cfr0%7C0%7C1524; dc_session_id=10_1732021958758.121041; c_dsid=11_1732021959427.558167; creativeSetApiNew=%7B%22toolbarImg%22%3A%22https%3A//img-home.csdnimg.cn/images/20230921102607.png%22%2C%22publishSuccessImg%22%3A%22https%3A//img-home.csdnimg.cn/images/20240229024608.png%22%2C%22articleNum%22%3A122%2C%22type%22%3A2%2C%22oldUser%22%3Atrue%2C%22useSeven%22%3Afalse%2C%22oldFullVersion%22%3Atrue%2C%22userName%22%3A%22MarkAdc%22%7D; waf_captcha_marker=2dacbb6b5a129a709c5df52b635ca0ddc99955e93551105b156eb3210fe33091; c_page_id=default; log_Id_pv=5291; Hm_lpvt_6bcd52f51e9b3dce32bec4a3997715ac=1732021980; _clsk=fcth9d%7C1732021983765%7C2%7C0%7Cs.clarity.ms%2Fcollect; dc_tos=sn78q6; log_Id_view=16967; log_Id_click=3758",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    }
    max_page = sys.argv[1] if len(sys.argv) == 2 else 1

    for i in range(int(max_page)):
        page = i + 1
        params = {
            "page": page,
            "size": "20",
            "businessType": "lately",
            "noMore": "false",
            "username": username,
        }
        job(params)
        pool.block()

        print("\n第{}页完成\n".format(page))
        time.sleep(3)


if __name__ == "__main__":
    main()
