from _typeshed import Incomplete
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Settings configuration for the application.

    This class uses Pydantic's BaseSettings to manage application settings
    from environment variables and a .env file.

    Attributes:
        model_config (SettingsConfigDict): Configuration for Pydantic settings.
        ADMIN_USER_EMAIL (str | None): The email of the admin user.
        ADMIN_USER_PASSWORD (str | None): The password of the admin user.
        AUTH_JWT_KEY (str | None): The key used for JWT authentication.
        AUTH_TOKEN_EXPIRATION (int): The expiration time for authentication tokens in seconds.
        REQUIRE_DEFAULT_AUTHORIZATION (bool): Flag to require default authorization.
    """
    model_config: Incomplete
    ADMIN_USER_EMAIL: str | None
    ADMIN_USER_PASSWORD: str | None
    AUTH_JWT_KEY: str | None
    AUTH_TOKEN_EXPIRATION: int
    REQUIRE_DEFAULT_AUTHORIZATION: bool

auth_settings: Incomplete
