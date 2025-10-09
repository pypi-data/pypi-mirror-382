from dataclasses import dataclass
from typing import List

@dataclass
class Owner:
    firstName: str
    lastName: str

@dataclass
class IbanInfo:
    bank: str
    depositNumber: str
    iban: str
    status: str
    owners: List[Owner]

@dataclass
class Card:
    number: str
    type: str
    ibanInfo: IbanInfo

@dataclass
class JibitTokens:
    access_token: str
    refresh_token: str
