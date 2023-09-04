from typing import Dict, List, Optional, TypedDict


class HeroBrief(TypedDict):
    heroId: int
    heroFightPower: int


class Skin(TypedDict):
    skinId: str
    expireTime: str
    szTitle: str
    iPrice: int
    iBuy: int
    szPriceDesc: str
    szDesc: str
    szHeroTitle: str
    szHeroAlias: str
    szSmallIcon: str
    szBigIcon: str
    iClass: int
    skin_worth: Optional[int]
    szClass: str
    heroSortFightPower: int
    unixTime: str
    acquireTime: str
    noAcquire: str


class SkinDetail(TypedDict):
    iHeroId: int
    iSkinId: int
    iLabelId: int
    szHeroAlias: str
    szTitle: str
    szLargeIcon: str
    szSmallIcon: str
    szAppendProp: str
    iBuy: int
    isHidden: int
    szDesc: str
    szClass: str
    iPrice: int
    skin_worth: Optional[int]
    szLabelTitle: str
    szIcon: str
    szHeroTitle: str
    classLabel: str
    goodsId: str
    classType: List[str]
    classTypeName: List[str]
    accessWay: str
    preUptime: int
    bigCover: str


class SkinDetailAdd(SkinDetail):
    level: int


class HeroType(TypedDict):
    typeKey: int
    heroType: str


class Hero(HeroType):
    url: str
    heroIcon: str
    name: str


class SkinType(TypedDict):
    classType: int
    classTypeName: str


class SkinCountInfo(TypedDict):
    notForSell: int
    totalValue: int
    owned: str
    totalSkinNum: int
    heroTypeList: List[HeroType]
    skinTypeList: List[SkinType]


class SkinInfo(TypedDict):
    heroList: Dict[str, HeroBrief]
    skinCountInfo: SkinCountInfo
    heroConfList: Dict[str, Hero]
    heroSkinList: List[Skin]
    sortedHeroSkinList: List[List[str]]
    heroSkinConfList: Dict[str, SkinDetail]
