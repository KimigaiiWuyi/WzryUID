from pathlib import Path

from gsuid_core.data_store import get_res_path

BG_PATH = Path(__file__).parent / 'bg'
MAIN_PATH = get_res_path('WzryUID')
AVATAR_PATH = MAIN_PATH / 'avatar'
SKILL_PATH = MAIN_PATH / 'skill'
EQUIP_PATH = MAIN_PATH / 'equip'
ICON_PATH = MAIN_PATH / 'icon'
SKIN_PATH = MAIN_PATH / 'skin'

TEMP_PATH = MAIN_PATH / 'temp'


def init_dir():
    for i in [
        MAIN_PATH,
        ICON_PATH,
        AVATAR_PATH,
        SKIN_PATH,
        TEMP_PATH,
        SKILL_PATH,
        EQUIP_PATH,
    ]:
        i.mkdir(parents=True, exist_ok=True)


init_dir()
