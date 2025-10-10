from typing import Any
from typing import ClassVar

from amsdal_models.builder.validators.options_validators import validate_options
from amsdal_utils.models.enums import ModuleType
from pydantic import field_validator
from pydantic.fields import Field

from amsdal.contrib.frontend_configs.models.frontend_config_skip_none_base import *  # noqa: F403


class FrontendConfigControlAction(FrontendConfigSkipNoneBase):  # noqa: F405
    __module_type__: ClassVar[ModuleType] = ModuleType.CONTRIB
    action: str = Field(title='Action')
    text: str = Field(title='Text')
    type: str = Field(title='Type')
    dataLayerEvent: str | None = Field(None, title='Data Layer Event')  # noqa: N815
    activator: str | None = Field(None, title='Activator')
    icon: str | None = Field(None, title='Icon')

    @field_validator('type')
    @classmethod
    def validate_value_in_options_type(cls: type, value: Any) -> Any:  # type: ignore # noqa: A003
        return validate_options(value, options=['action-button', 'arrow-next', 'arrow-prev', 'text-next', 'text-prev'])

    @field_validator('action', mode='after')
    @classmethod
    def validate_action(cls, v: str) -> str:
        """
        Validates the action string to ensure it is one of the allowed values.

        This method checks if the action string starts with 'navigate::' or is one of the predefined
        actions. If the action string is invalid, it raises a ValueError.

        Args:
            cls: The class this method is attached to.
            v (str): The action string to validate.

        Returns:
            str: The validated action string.

        Raises:
            ValueError: If the action string is not valid.
        """
        if not v.startswith('navigate::') and v not in [
            'goPrev',
            'goNext',
            'goNextWithSubmit',
            'submit',
            'submitWithDataLayer',
        ]:
            msg = 'Action must be one of: goPrev, goNext, goNextWithSubmit, submit, submitWithDataLayer, navigate::{string}'  # noqa: E501
            raise ValueError(msg)
        return v
