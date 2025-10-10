__app_name__ = "material_ai"
__version__ = "1.0.0"

from .app import get_app
from .oauth import (
    IOAuthService,
    OAuthRedirectionResponse,
    OAuthUserDetail,
    OAuthSuccessResponse,
)
from .oauth import OAuthErrorResponse, SSOConfig, handle_httpx_errors
