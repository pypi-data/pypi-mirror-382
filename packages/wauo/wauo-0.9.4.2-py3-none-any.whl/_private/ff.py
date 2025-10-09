import os
from pathlib import Path

from loguru import logger

for file in Path.cwd().glob('*'):
    if file.is_file():
        src = str(file)
        dst = src.replace(file.suffix, ".wav")
        logger.info(src)
        cmd = f'ffmpeg -i "{src}" -vn -acodec pcm_s16le -ar 16000 -ac 2 -y "{dst}"'
        os.system(cmd)
        logger.success(dst)
