import random
import time

from wauo.utils import PoolWait, PoolMan, cprint

pool_wait = PoolWait()
pool_man = PoolMan()


def download(tid):
    cprint("正在执行... {} 任务".format(tid), "black")
    time.sleep(random.uniform(2, 3))
    cprint("{} 已完成".format(tid), "green")


def test():
    t1 = time.time()

    pool = pool_man
    for i in range(22):
        pool.add(download, "商品{}".format(i + 1))
        print(pool.is_running())
    pool.close()

    print(pool.is_running())

    t2 = time.time()
    cprint("耗时：{:.2f}".format(t2 - t1), "red")


if __name__ == '__main__':
    test()
