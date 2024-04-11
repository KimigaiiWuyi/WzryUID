from io import BytesIO
from pathlib import Path
from typing import Tuple, Union, Optional, overload

import aiofiles
from PIL import Image
from httpx import AsyncClient
from gsuid_core.logger import logger


@overload
async def download_file(
    url: str,
    path: Path,
    name: str,
    size: Optional[Tuple[int, int]],
) -> Image.Image:
    pass


@overload
async def download_file(
    url: str,
    path: Path,
    name: str,
    size: Optional[Tuple[int, int]] = None,
) -> Union[Tuple[str, Path, str], None]:
    pass


async def download_file(
    url: str,
    path: Path,
    name: str,
    size: Optional[Tuple[int, int]] = None,
) -> Union[Image.Image, Tuple[str, Path, str], None]:
    file_path = path / name
    if file_path.exists():
        if size:
            return Image.open(file_path).resize(size)
        return Image.open(file_path)

    async with AsyncClient() as sess:
        try:
            logger.info(f'[wzry]开始下载: {name} | 地址: {url}')
            resp = await sess.get(url)
            content = resp.read()
            logger.info(f'[wzry]下载成功: {name}')
        except:  # noqa
            logger.warning(f"[wzry]{name}下载失败")
            return url, path, name

    async with aiofiles.open(path / name, "wb") as f:
        await f.write(content)
        stream = BytesIO(content)
        if size:
            return Image.open(stream).resize(size)
        else:
            return Image.open(stream)
