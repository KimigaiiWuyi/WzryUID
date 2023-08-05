from pathlib import Path

from gsuid_core.data_store import get_res_path

BG_PATH = Path(__file__).parent / 'bg'
MAIN_PATH = get_res_path('WzryUID')
AVATAR_PATH = MAIN_PATH / 'avatar'
ICON_PATH = MAIN_PATH / 'icon'


def init_dir():
    for i in [
        MAIN_PATH,
        ICON_PATH,
        AVATAR_PATH,
    ]:
        i.mkdir(parents=True, exist_ok=True)


init_dir()
