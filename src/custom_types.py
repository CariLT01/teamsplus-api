
from typing import TypedDict, NotRequired
from typing import Any

class AuthenticationDataReturnType(TypedDict):
    id: int
    username: str
    favorites: str
    ownedThemes: str
    password: str
    publicKey: str
    privateKey: bytes
    iv: str|None

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

class HTTPRequestResponseDict(TypedDict):
    success: bool
    message: str
    httpStatus: int
    data: NotRequired[Any]


class EncryptionProviderDataDict(TypedDict):
    body: str
    iv: str
    signature: str
    keys: dict[int, str]  # keys for each user ID
    author: int  # ID of the author of the message

class EncryptionProviderResultDict(TypedDict):
    success: bool
    message: str
    httpStatus: int
    data: EncryptionProviderDataDict
    note: str | None  # Optional note for failed encryption/decryption attempts`

class ThemeSearchFinalListEntryDict(TypedDict):
    name: str
    desc: str
    data: str
    author: str
    stars: int