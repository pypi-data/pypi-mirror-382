import random
import threading
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed

from loguru import logger


def get_results(fs: list, timeout=None):
    """处理线程任务，有序获取（先返回的靠前）所有线程的返回值（异常的线程、假值除外）"""
    results = []
    try:
        for v in as_completed(fs, timeout=timeout):
            try:
                result = v.result()
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(e)
    except Exception as e:
        logger.error(e)
    return results


class BasePool(ABC):
    def __init__(self, speed=5, limit: int = None):
        self.speed = speed
        self.pool = ThreadPoolExecutor(max_workers=self.speed)
        self.count = 0
        self.max_count = limit or speed

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self, wait=True, cancel_futures=False):
        """释放资源"""
        self.pool.shutdown(wait=wait, cancel_futures=cancel_futures)

    def done(self, future):
        """线程的回调函数"""
        try:
            future.result()
        except Exception as e:
            logger.error("Thread Error => {}".format(e))

    @abstractmethod
    def todo(self, func, *args, **kwargs):
        pass

    def todos(self, func, *some):
        for args in zip(*some):
            self.todo(func, *args)


class WaitPool(BasePool):
    """需要等待同一批的线程结束后，才能分配下一批新的线程"""

    def todo(self, func, *args, **kwargs):
        """核心"""
        if self.count >= self.max_count:
            self.pool.shutdown()
            self.pool = ThreadPoolExecutor(max_workers=self.speed)
            self.count = 0
        future = self.pool.submit(func, *args, **kwargs)
        self.count += 1
        future.add_done_callback(self.done)


class SpeedPool(BasePool):
    def __init__(self, speed=5, limit: int = None):
        """
        当池子里有线程结束时，新的线程可以立刻进来
        Args:
            speed: 线程并发数
            limit: 线程限制数
        """
        super().__init__(speed, limit)
        self.add_task = threading.Condition()
        self.running_futures = []

    def todo(self, func, *args, **kwargs):
        """核心"""
        with self.add_task:
            while self.count >= self.max_count:
                logger.info("wait......{}".format(args))
                self.add_task.wait()

            future = self.pool.submit(func, *args, **kwargs)
            self.count += 1
            self.running_futures.append(future)
            future.add_done_callback(self.done)

    def done(self, future):
        """线程的回调函数"""
        super().done(future)

        with self.add_task:
            self.count -= 1
            self.running_futures.remove(future)
            self.add_task.notify()

    def running(self):
        """是否还有任务在运行"""
        for f in self.running_futures:
            if f.is_running():
                return True
        return False


def task(name):
    uid = "任务{}".format(name)
    while True:
        time.sleep(1)
        logger.warning("{}执行中...".format(uid))
        n = random.randint(1, 10)
        if n == 10:
            raise Exception("It is {}".format(uid))
        if n == 2:
            logger.success("...{}完成了".format(uid))
            break


if __name__ == "__main__":
    pool = SpeedPool()
    for i in range(10):
        pool.todo(task, i + 1)
