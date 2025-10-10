from typing import Any
from typing import ClassVar

from amsdal_models.classes.model import Model
from amsdal_utils.models.enums import ModuleType
from pydantic.fields import Field

from amsdal.contrib.auth.models.permission import *  # noqa: F403


class User(Model):
    __module_type__: ClassVar[ModuleType] = ModuleType.CONTRIB
    email: str = Field(title='Email')
    password: bytes = Field(title='Password (hash)')
    permissions: list['Permission'] | None = Field(None, title='Permissions')  # noqa: F405

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f'User(email={self.email})'

    async def apre_update(self) -> None:
        import bcrypt

        original_object = await self.arefetch_from_db()
        password = self.password
        if original_object.password and password is not None:
            if isinstance(password, str):
                password = password.encode('utf-8')
            try:
                if not bcrypt.checkpw(password, original_object.password):
                    self.password = password
            except ValueError:
                hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
                self.password = hashed_password

    @property
    def display_name(self) -> str:
        """
        Returns the display name of the user.

        This method returns the email of the user as their display name.

        Returns:
            str: The email of the user.
        """
        return self.email

    def post_init(self, *, is_new_object: bool, kwargs: dict[str, Any]) -> None:
        """
        Post-initializes a user object by validating email and password, and hashing the password.

        This method checks if the email and password are provided and valid. If the object is new,
        it hashes the password and sets the object ID to the lowercased email.

        Args:
            is_new_object (bool): Indicates if the object is new.
            kwargs (dict[str, Any]): The keyword arguments containing user details.

        Raises:
            UserCreationError: If the email or password is invalid.
        """
        import bcrypt

        from amsdal.contrib.auth.errors import UserCreationError

        email = kwargs.get('email', None)
        password = kwargs.get('password', None)
        if email is None or email == '':
            msg = "Email can't be empty"
            raise UserCreationError(msg)
        if password is None or password == '':
            msg = "Password can't be empty"
            raise UserCreationError(msg)
        kwargs['email'] = email.lower()
        if is_new_object and '_metadata' not in kwargs:
            if isinstance(password, str):
                password = password.encode('utf-8')
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
            self.password = hashed_password
            self._object_id = email.lower()

    def pre_create(self) -> None:
        """
        Pre-creates a user object.

        This method is a placeholder for any pre-creation logic that needs to be executed
        before a user object is created.
        """
        pass

    def pre_update(self) -> None:
        import bcrypt

        original_object = self.refetch_from_db()
        password = self.password
        if original_object.password and password is not None:
            if isinstance(password, str):
                password = password.encode('utf-8')
            try:
                if not bcrypt.checkpw(password, original_object.password):
                    self.password = password
            except ValueError:
                hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
                self.password = hashed_password
