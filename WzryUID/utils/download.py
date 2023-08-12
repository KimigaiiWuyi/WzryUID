from io import BytesIO
from pathlib import Path
from typing import Tuple, Union, Optional, overload

import aiofiles
from PIL import Image
from gsuid_core.logger import logger
from aiohttp.client import ClientSession
from aiohttp.client_exceptions import ClientConnectorError


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
    async with ClientSession() as sess:
        try:
            async with sess.get(url) as res:
                content = await res.read()
        except ClientConnectorError:
            logger.warning(f"[wzry]{name}下载失败")
            return url, path, name
        async with aiofiles.open(path / name, "wb") as f:
            await f.write(content)
            if size:
                stream = BytesIO(content)
                return Image.open(stream).resize(size)
