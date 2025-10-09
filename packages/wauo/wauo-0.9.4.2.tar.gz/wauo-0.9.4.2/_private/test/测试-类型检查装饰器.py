import time

from wauo.utils import type_check


@type_check
def add(a: int, b: int) -> int:
    c = a + b
    return c


if __name__ == "__main__":
    s1 = '"demo1"'
    s2 = "'demo2'"
    s3 = """demo3"""
    time.sleep(3)
    print(s1, s2, s3)
    add([], {})
