"""
Configuration cho System Integrator (refactor dùng Pydantic Settings)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class SystemIntegratorSettings(BaseSettings):
    # JWT Configuration
    JWT_ALGORITHM: str = "HS256"
    SI_DEFAULT_TOKEN_EXPIRY_HOURS: int = 24
    SI_SYSTEM_USER_TOKEN_SECRET: str = "system-integrator-user-token-secret-2024"

    # Default Client Configuration
    SI_DEFAULT_CLIENT_ID: str = "royalty-integrator-001"
    SI_DEFAULT_CLIENT_SECRET: str = "royalty-secret-2024"

    # Service URLs
    AUTH_SERVICE_URL: str = "http://auth-service:8100"
    USER_SERVICE_URL: str = "http://user-service:8001"

    # Security Settings
    SI_ENABLE_TOKEN_REVOCATION: bool = False
    SI_MAX_TOKEN_PER_CLIENT: int = 10

    # App env
    APP_ENV: str = "local"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


system_integrator_settings = SystemIntegratorSettings()


class SystemIntegratorConfig:
    """Configuration cho System Integrator features (compatibility layer)"""

    # JWT Configuration
    JWT_ALGORITHM = system_integrator_settings.JWT_ALGORITHM
    DEFAULT_TOKEN_EXPIRY_HOURS = system_integrator_settings.SI_DEFAULT_TOKEN_EXPIRY_HOURS
    SYSTEM_USER_TOKEN_SECRET = (
        system_integrator_settings.SI_SYSTEM_USER_TOKEN_SECRET
    )

    # Default Client Configuration
    DEFAULT_CLIENT_ID = system_integrator_settings.SI_DEFAULT_CLIENT_ID
    DEFAULT_CLIENT_SECRET = system_integrator_settings.SI_DEFAULT_CLIENT_SECRET

    # Service URLs
    AUTH_SERVICE_URL = system_integrator_settings.AUTH_SERVICE_URL
    USER_SERVICE_URL = system_integrator_settings.USER_SERVICE_URL

    # Security Settings
    ENABLE_TOKEN_REVOCATION = system_integrator_settings.SI_ENABLE_TOKEN_REVOCATION
    MAX_TOKEN_PER_CLIENT = system_integrator_settings.SI_MAX_TOKEN_PER_CLIENT

    # Permission Settings
    DEFAULT_SCOPES = [
        "royalty:read",
        "royalty:write",
        "news:read",
        "user:read",
    ]

    # Endpoint Paths
    ENDPOINT_PATHS = {
        "AUTH_AUTHENTICATE": "system-integrator/authenticate",
        "AUTH_VALIDATE": "system-integrator/validate",
        "USER_INTROSPECT": "system-integrator/introspect",
        "USER_CHECK_PERMISSION": "system-integrator/check-permission",
    }

    @classmethod
    def get_endpoint_url(cls, service: str, endpoint: str) -> str:
        """Get full URL cho endpoint"""
        base_urls = {
            "auth": cls.AUTH_SERVICE_URL,
            "user": cls.USER_SERVICE_URL,
        }

        base_url = base_urls.get(service.lower())
        if not base_url:
            raise ValueError(f"Unknown service: {service}")

        endpoint_path = cls.ENDPOINT_PATHS.get(endpoint)
        if not endpoint_path:
            raise ValueError(f"Unknown endpoint: {endpoint}")

        return f"{base_url.rstrip('/')}/{endpoint_path}"

    @classmethod
    def is_development_mode(cls) -> bool:
        """Check if running in development mode"""
        return (system_integrator_settings.APP_ENV or "local").lower() in [
            "local",
            "development",
            "dev",
        ]
