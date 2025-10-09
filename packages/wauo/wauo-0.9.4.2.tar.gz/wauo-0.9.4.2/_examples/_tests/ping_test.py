import asyncio
import subprocess
import platform
from loguru import logger




async def is_ip_online(ip):
    await asyncio.sleep(1)
    system_name = platform.system().lower()
    if system_name == 'windows':
        command = ['ping', '-n', '1', '-w', '1000', ip]
    else:
        command = ['ping', '-c', '1', '-W', '1', ip]
    try:
        subprocess.check_output(command, universal_newlines=True)
        return "在线"
    except subprocess.CalledProcessError:
        return "不在线"

async def main():
    ip = "192.168.1.1"
    tasks = [
        is_ip_online(ip)
        for _ in range(4)
    ]
    results = await asyncio.gather(*tasks)
    for r in results:
        print(r)

if __name__ == '__main__':
    logger.debug("开始计时")
    asyncio.run(main())
    logger.debug("结束")
