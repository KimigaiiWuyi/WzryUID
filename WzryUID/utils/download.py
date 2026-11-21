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
    from io import BytesIO

    file_path = path / name
    # 命中缓存前先校验是否为有效图片（旧版曾把 404 的 XML 错误页当成图片缓存，
    # 导致后续每次 Image.open 都抛 UnidentifiedImageError）
    if file_path.exists():
        try:
            with Image.open(file_path) as _im:
                _im.verify()
            if size:
                with Image.open(file_path) as _im:
                    return _im.resize(size)
            return Image.open(file_path)
        except Exception:
            logger.warning(f'[wzry]缓存文件损坏, 重新下载: {name}')
            try:
                file_path.unlink()
            except OSError:
                pass

    async with AsyncClient() as sess:
        try:
            logger.info(f'[wzry]开始下载: {name} | 地址: {url}')
            resp = await sess.get(url)
            content = resp.content
            # 校验 HTTP 状态与图片内容，避免把错误页写进缓存
            if resp.status_code != 200:
                logger.warning(f'[wzry]{name}下载失败: HTTP {resp.status_code}')
                return url, path, name
            with Image.open(BytesIO(content)) as _im:
                _im.verify()
            logger.info(f'[wzry]下载成功: {name}')
        except Exception:
            logger.warning(f"[wzry]{name}下载失败或内容非图片")
            return url, path, name

    async with aiofiles.open(path / name, "wb") as f:
        await f.write(content)
        stream = BytesIO(content)
        if size:
            return Image.open(stream).resize(size)
        return Image.open(stream)
