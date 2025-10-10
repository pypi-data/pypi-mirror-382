from datetime import UTC
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import ClassVar

import jwt
from amsdal_models.classes.model import Model
from amsdal_utils.models.enums import ModuleType
from pydantic.fields import Field


class LoginSession(Model):
    __module_type__: ClassVar[ModuleType] = ModuleType.CONTRIB
    email: str = Field(title='Email')
    password: str = Field(title='Password (hash)')
    token: str | None = Field(None, title='Token')

    @property
    def display_name(self) -> str:
        """
        Returns the display name of the user.

        This method returns the email of the user as their display name.

        Returns:
            str: The email of the user.
        """
        return self.email

    def pre_init(self, *, is_new_object: bool, kwargs: dict[str, Any]) -> None:
        """
        Pre-initializes a user object by validating email and password, and generating a JWT token.

        This method checks if the object is new and validates the provided email and password.
        If the email and password are valid, it generates a JWT token and adds it to the kwargs.

        Args:
            is_new_object (bool): Indicates if the object is new.
            kwargs (dict[str, Any]): The keyword arguments containing user details.

        Raises:
            AuthenticationError: If the email or password is invalid.
        """
        if not is_new_object or '_metadata' in kwargs:
            return
        from amsdal.contrib.auth.errors import AuthenticationError
        from amsdal.contrib.auth.settings import auth_settings

        email = kwargs.get('email', None)
        password = kwargs.get('password', None)
        if not email:
            msg = "Email can't be empty"
            raise AuthenticationError(msg)
        if not password:
            msg = "Password can't be empty"
            raise AuthenticationError(msg)
        lowercased_email = email.lower()

        if not auth_settings.AUTH_JWT_KEY:
            msg = 'JWT key is not set'
            raise AuthenticationError(msg)

        expiration_time = datetime.now(tz=UTC) + timedelta(seconds=auth_settings.AUTH_TOKEN_EXPIRATION)
        token = jwt.encode(
            {'email': lowercased_email, 'exp': expiration_time},
            key=auth_settings.AUTH_JWT_KEY,  # type: ignore[arg-type]
            algorithm='HS256',
        )
        kwargs['token'] = token

    def pre_create(self) -> None:
        import bcrypt

        from amsdal.contrib.auth.errors import AuthenticationError
        from amsdal.contrib.auth.models.user import User

        user = User.objects.filter(email=self.email).latest().first().execute()

        if not user:
            msg = 'User not found'
            raise AuthenticationError(msg)

        if not bcrypt.checkpw(self.password.encode(), user.password):
            msg = 'Invalid password'
            raise AuthenticationError(msg)

        self.password = 'validated'

    def pre_update(self) -> None:
        from amsdal.contrib.auth.errors import AuthenticationError

        msg = 'Update not allowed'
        raise AuthenticationError(msg)

    async def apre_create(self) -> None:
        import bcrypt

        from amsdal.contrib.auth.errors import AuthenticationError
        from amsdal.contrib.auth.models.user import User

        user = await User.objects.filter(email=self.email).latest().first().aexecute()

        if not user:
            msg = 'User not found'
            raise AuthenticationError(msg)

        if not bcrypt.checkpw(self.password.encode(), user.password):
            msg = 'Invalid password'
            raise AuthenticationError(msg)

        self.password = 'validated'

    async def apre_update(self) -> None:
        from amsdal.contrib.auth.errors import AuthenticationError

        msg = 'Update not allowed'
        raise AuthenticationError(msg)
