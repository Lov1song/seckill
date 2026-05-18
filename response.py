from typing import Any, Optional
from pydantic import BaseModel

class ApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None

    @classmethod
    def ok(cls, data: Any = None, message: str = "success"):
        return cls(code=200, message=message, data=data)

    @classmethod
    def fail(cls, code: int = 400, message: str = "failed"):
        return cls(code=code, message=message, data=None)