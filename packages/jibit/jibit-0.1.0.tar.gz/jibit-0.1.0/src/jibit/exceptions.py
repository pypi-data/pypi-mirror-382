from enum import Enum

class JibitErrorCode(Enum):
    INVALID_CARD = "JIBIT_400_INVALID_CARD"
    UNAUTHORIZED = "JIBIT_401_UNAUTHORIZED"
    SERVICE_UNAVAILABLE = "JIBIT_503_UNAVAILABLE"
    UNKNOWN_ERROR = "JIBIT_500_UNKNOWN_ERROR"

    def __str__(self) -> str:
        return self.value

class JibitException(Exception):
    def __init__(self, code: JibitErrorCode, detail: str, http_status: int = 500):
        self.code = code
        self.detail = detail
        self.http_status = http_status
        super().__init__(f"[{self.code}] {self.detail}")
