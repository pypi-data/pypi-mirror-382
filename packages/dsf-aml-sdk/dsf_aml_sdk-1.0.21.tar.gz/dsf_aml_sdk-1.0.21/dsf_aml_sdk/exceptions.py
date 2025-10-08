# ============================================
# dsf_aml_sdk/exceptions.py
# ============================================
from typing import Optional

class AMLSDKError(Exception):
    pass

class ValidationError(AMLSDKError):
    pass

class LicenseError(AMLSDKError):
    pass

class APIError(AMLSDKError):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code