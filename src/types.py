
from typing import TypedDict

class AuthenticationDataReturnType(TypedDict):
    id: int
    username: str
    favorites: str
    ownedThemes: str
    password: str
    publicKey: str
    privateKey: str
    iv: str

class ThemeDataReturnType(TypedDict):
    id: int
    themeName: str
    description: str
    data: str
    author: str
    stars: int
class AuthenticationToken(TypedDict):
    exp: int
    username: str
    id: int

## Theme

class TDThemeData_FontsDictType(TypedDict):
    fontFamily: str
    imports: str

class TDThemeData_DataFieldDictType(TypedDict):
    varColors: dict[str, str]
    classColors: dict[str, str]
    fonts: TDThemeData_FontsDictType
    otherSettings: dict[str, str]
    twemojiSupport: bool

class TDThemeDataDict(TypedDict):
    data: TDThemeData_DataFieldDictType
    name: str
    data_version: int

## Auth provider

class AuthProviderResultDict(TypedDict):
    success: bool
    message: str
    httpStatus: int
    data: str | None