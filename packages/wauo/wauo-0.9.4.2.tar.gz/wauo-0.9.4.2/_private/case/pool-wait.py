import time
from concurrent.futures import ThreadPoolExecutor, wait

from wauo.utils import PoolMan

pool = ThreadPoolExecutor(max_workers=5)
pool2 = PoolMan(speed=5)


def job(name):
    for i in range(5):
        print("{}-{}".format(name, i + 1))
        time.sleep(1)


def main():
    fs = []
    for i in range(5):
        f = pool.submit(job, name="任务{}".format(i + 1))
        fs.append(f)
    wait(fs)

    pool.submit(job, "9号")


if __name__ == "__main__":
    main()
