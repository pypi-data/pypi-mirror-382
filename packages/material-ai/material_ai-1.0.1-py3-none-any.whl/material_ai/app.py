import threading
import logging
import os
import json
from fastapi import FastAPI, Request, HTTPException, Response
from google.adk.cli.fast_api import get_fast_api_app
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from .config import get_config
from fastapi.staticfiles import StaticFiles
from .exec import ConfigError, UnauthorizedException
import time
import http.cookies
from .auth import _remove_cookies
from .oauth import get_oauth, OAuthErrorResponse
from .log_config import setup_structured_logging
from .oauth import oauth_user_details_context
from .auth import (
    verify_user_details,
    get_oauth_service,
    get_ui_configuration,
    get_feedback_handler,
)
from .auth import FeedbackHandler
from .oauth import OAuthUserDetail, IOAuthService
from .ui_config import get_ui_config
from .request import FeedbackRequest

from . import __app_name__, __version__

_lock = threading.Lock()
_logger = logging.getLogger(__name__)
_app_instance: FastAPI | None = None
_lock = threading.Lock()

STATIC_DIR = f"{os.path.dirname(os.path.abspath(__file__))}/ui/dist"
UI_CONFIG_YAML = f"{os.path.dirname(os.path.abspath(__file__))}/ui/ui_config.yaml"
AGENT_DIR = f"{os.path.dirname(os.path.abspath(__file__))}/agents"
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1",
    "http://127.0.0.1:5173",
]


class AddXAppHeaderMiddleware(BaseHTTPMiddleware):
    """Adds the X-App header, with app name and version, to all responses."""

    def __init__(self, app, app_name: str, app_version: str):
        super().__init__(app)
        self.app_name = app_name
        self.app_version = app_version

    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-AppInfo"] = f"{self.app_name}/{self.app_version}"
        return response


class AuthMiddleware(BaseHTTPMiddleware):
    """Adds the X-App header, with app name and version, to all responses."""

    def __init__(self, app, oauth_service: IOAuthService):
        super().__init__(app)
        self.oauth_service = oauth_service

    async def dispatch(self, request, call_next):
        route = request.url.path
        EXCLUDED_PATHS = [
            "/",
            "/login",
            "/health",
            "/config",
            "/auth",
            "/icon.svg",
            "/favicon.ico",
            "/.well-known/appspecific/com.chrome.devtools.json",
        ]
        EXCLUDED_PREFIXES = ["/assets/"]
        is_excluded_path = route in EXCLUDED_PATHS or any(
            route.startswith(prefix) for prefix in EXCLUDED_PREFIXES
        )

        if is_excluded_path:
            return await call_next(request)

        cookies_header = request.headers.get("cookie")

        try:
            if not cookies_header:
                raise UnauthorizedException()

            cookies = http.cookies.SimpleCookie()
            cookies.load(cookies_header)

            if cookies.get("refresh_token") == None:
                raise UnauthorizedException()

            if route == "/user":
                return await call_next(request)

            if cookies.get("access_token") == None:
                raise UnauthorizedException()
            if cookies.get("user_details") == None:
                raise UnauthorizedException()

            auth = self.oauth_service

            access_token_cookie = cookies.get("access_token")
            oauth_response = await auth.sso_verify_access_token(
                access_token_cookie.value
            )

            if not oauth_response:
                raise UnauthorizedException()

            if isinstance(oauth_response, OAuthErrorResponse):
                raise UnauthorizedException()

            uid = str(oauth_response)

            # If we want to cross check if given user can call this API
            # We dont want other actors to modify user session
            if "users" in route:
                user_id = extract_user_id_from_path(route)
                if user_id and user_id != uid:
                    raise UnauthorizedException()

            if route != "/run":
                return await call_next(request)

            user_details_cookie = cookies.get("user_details")
            decoded_user_details = verify_user_details(user_details_cookie.value)
            if decoded_user_details == None:
                raise UnauthorizedException()

            user_details = OAuthUserDetail(**json.loads(decoded_user_details))

            oauth_user_details_context.set(user_details)
            body_bytes = await request.body()

            async def receive():
                return {"type": "http.request", "body": body_bytes}

            json_payload = json.loads(body_bytes.decode("utf-8"))
            if "user_id" in json_payload and json_payload["user_id"] != uid:
                raise UnauthorizedException()
            new_request = Request(request.scope, receive)
            return await call_next(new_request)

        except UnauthorizedException as e:
            response = Response(status_code=401, content="Unauthorized")
            _remove_cookies(response)
            return response
        except Exception as e:
            _logger.error(
                f"ERROR: Error decoding JSON response from {route}: {e}", exc_info=e
            )
            response = Response(status_code=500, content="Internal Server Error")
            return response


async def on_feedback(_: FeedbackRequest):
    return Response(status_code=200)


def _setup_app(
    app: FastAPI,
    oauth_service: IOAuthService = None,
    ui_config_yaml: str = None,
    feedback_handler: FeedbackHandler = None,
) -> None:
    """
    Configures the FastAPI application with middleware, logging,
    based on the provided configuration settings. This setup is intended for use in environments
    such as GKE or similar platforms that support structured log parsing. Debug mode adjustments
    and security considerations are also applied. API routes are registered during setup.

    Args:
        app (FastAPI): The FastAPI application instance to configure.
        oauth_service (IOAuthService, optional): An instance of the OAuth
            service for authentication. Defaults to GoogleOAuthService.
        ui_config_yaml (str): The file path to the UI configuration YAML.
        feedback_handler: A handler function to handle user feedback

    Raises:
        RuntimeError: If the configuration is invalid or cannot be loaded.
    """
    # If we can't configure the app, exit immediately
    try:
        config = get_config()
    except ConfigError as e:
        raise RuntimeError("Bad configuration") from e  # lol :P

    json_logs_enabled = False if config.general.debug else True

    # Setup logging
    setup_structured_logging(
        app_name=__app_name__,
        enable_json_formatter=json_logs_enabled,
        log_level=logging.DEBUG if config.general.debug else logging.INFO,
    )

    ui_config = get_ui_config(ui_config_yaml)

    def override_get_oauth_service() -> IOAuthService:
        if oauth_service == None:
            return get_oauth()
        return oauth_service

    def override_get_ui_configuration() -> IOAuthService:
        return ui_config

    def override_get_feedback_handler() -> FeedbackHandler:
        if feedback_handler == None:
            return on_feedback
        return feedback_handler

    app.dependency_overrides[get_oauth_service] = override_get_oauth_service
    app.dependency_overrides[get_ui_configuration] = override_get_ui_configuration
    app.dependency_overrides[get_feedback_handler] = override_get_feedback_handler

    # Custom header middleware
    app.add_middleware(AuthMiddleware, oauth_service=override_get_oauth_service())
    app.add_middleware(
        AddXAppHeaderMiddleware,
        app_name=__app_name__,
        app_version=__version__,
    )
    app.add_middleware(SessionMiddleware, secret_key=config.sso.session_secret_key)
    # Custom exception handler
    app.add_exception_handler(HTTPException, http_exception_cookie_clearer)

    from .api import router as core_router

    app.include_router(core_router)
    app.mount("/", StaticFiles(directory=STATIC_DIR), name="static")

    # Apply cors middleware in debug mode
    if config.general.debug:
        _logger.debug("App running in DEBUG mode")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


def get_app(
    agent_dir: str = AGENT_DIR,
    oauth_service: IOAuthService = None,
    ui_config_yaml: str = UI_CONFIG_YAML,
    feedback_handler: FeedbackHandler = None,
):
    """Factory function to get the singleton FastAPI application instance.

    This function ensures that only one instance of the FastAPI application is
    created during the application's lifecycle. It uses a thread-safe lock to
    manage instantiation, guaranteeing a single, shared app object. This
    approach also prevents circular import issues by providing a centralized
    access point.

    Args:
        agent_dir (str): The directory path for the agent.
        oauth_service (IOAuthService, optional): An instance of the OAuth
            service for authentication. Defaults to GoogleOAuthService.
        ui_config_yaml (str): The file path to the UI configuration YAML.
        feedback_handler: A handler function to handle user feedback

    Returns:
        FastAPI: The singleton instance of the FastAPI application.
    """
    global _app_instance
    with _lock:
        if _app_instance is None:
            config = get_config()
            app = get_fast_api_app(
                agent_dir=agent_dir,
                web=False,
                allow_origins=ALLOWED_ORIGINS if config.general.debug else [],
                session_db_url=config.adk.session_db_url,
            )
            _setup_app(app, oauth_service, ui_config_yaml, feedback_handler)
            _app_instance = app

        return _app_instance


async def http_exception_cookie_clearer(request: Request, exc: HTTPException):
    """
    Catches any HTTPException. If the status code is 401 (Unauthorized),
    it clears authentication cookies before returning the error response.
    """
    # If the exception is a 401 Unauthorized, clear the cookies
    if exc.status_code == 401:
        # Create a standard JSON response for the 401 error
        response = Response(status_code=401, content="Unauthorized")
        _remove_cookies(response)
        return response

    # For all other HTTPExceptions, fall back to the default behavior
    return Response(
        status_code=exc.status_code,
    )


def extract_user_id_from_path(path: str) -> str | None:
    """
    If the segment '/users/' exists in a URL path, this function extracts
    the very next segment, which is assumed to be the user ID.

    Args:
        path: The URL path string (e.g., "/apps/my-app/users/12312321/sessions").

    Returns:
        The user ID as a string if found, otherwise None.
    """
    try:
        parts = path.strip("/").split("/")

        users_index = parts.index("users")

        if users_index + 1 < len(parts):
            return parts[users_index + 1]

        return None

    except ValueError:
        return None
