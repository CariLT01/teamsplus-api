"""
Custom types needed for MyPy type checker
"""

from typing import TypedDict, NotRequired
from typing import Any

class AuthenticationDataReturnType(TypedDict):
    '''
    Return type for user data when reading from database
    '''
    id: int
    username: str
    favorites: str
    ownedThemes: str
    password: str
    publicKey: str
    privateKey: bytes
    iv: str|None
    coins: int

class ThemeDataReturnType(TypedDict):
    '''
    Return type for data about a theme
    '''
    id: int
    themeName: str
    description: str
    data: str
    author: str
    stars: int
class AuthenticationToken(TypedDict):
    '''
    Return type for JWT token payload
    '''
    exp: int
    username: str
    id: int

## Theme

class TDThemeData_FontsDictType(TypedDict):
    '''
    Sub-type
    '''
    fontFamily: str
    imports: str

class TDThemeData_DataFieldDictType(TypedDict):
    '''
    Sub-type
    '''
    varColors: dict[str, str]
    classColors: dict[str, str]
    fonts: TDThemeData_FontsDictType
    otherSettings: dict[str, str]
    twemojiSupport: bool

class TDThemeDataDict(TypedDict):
    '''
    Type definition for theme
    '''
    data: TDThemeData_DataFieldDictType
    name: str
    data_version: int

## Auth provider

class HTTPRequestResponseDict(TypedDict):
    '''
    Generic return type for HTTP request
    '''
    success: bool
    message: str
    httpStatus: int
    data: NotRequired[Any]


class EncryptionProviderDataDict(TypedDict):
    '''
    Input? type for encryption function
    '''
    body: str
    iv: str
    signature: str
    keys: dict[int, str]  # keys for each user ID
    author: int  # ID of the author of the message

class EncryptionProviderResultDict(TypedDict):
    '''
    Return type for encryption function
    '''
    success: bool
    message: str
    httpStatus: int
    data: EncryptionProviderDataDict
    note: str | None  # Optional note for failed encryption/decryption attempts`

class ThemeSearchFinalListEntryDict(TypedDict):
    '''
    Type definition
    '''
    name: str
    desc: str
    data: str
    author: str
    stars: int

class GOL_HTTP_Data(TypedDict):
    '''
    Type def
    '''

    options: list[str]
    content: str
    eventId: int



class GameOfLife_HTTPGetEventReturnType(TypedDict):
    '''
    Type definition for return type of LifeEvent get request
    '''

    success: bool
    message: str
    data: NotRequired[GOL_HTTP_Data | None]
    httpStatus: int