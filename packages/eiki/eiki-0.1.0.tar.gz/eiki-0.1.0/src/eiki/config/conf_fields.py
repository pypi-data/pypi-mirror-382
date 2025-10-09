import os
from typing import TypeVar, Generic, Type, Any, cast
from pydantic import Field

# generic type variable for environment variable type
E = TypeVar('E')

class ENV(Generic[E]):
    """Class to represent an environment variable with type casting."""
    _type_hint: Type[Any] = str  # Default type hint
    
    def __class_getitem__(cls, item: Type[Any]):
        """Capture the type when using ENV[SomeType] syntax"""
        
        # Create a new class with the captured type information
        new_cls = type(cls.__name__, (cls,), {'_type_hint': item})
        return new_cls
    
    def __new__(cls, name: str) -> E:
        """Fetch and cast the environment variable value.

        On instantiation, this class retrieves the value of the specified environment variable
        and casts it to the type specified in the generic parameter. Meaning the class returned
        will have the correct type for the environment variable's value.
        """
        # check if instantiated directly and reject
        if cls is ENV:
            raise TypeError("Cannot instantiate ENV directly. Use ENV[Type](name) instead.")
        
        # Get the environment variable value and cast it
        try:
            env_value = os.environ[name]
            return cls._cast_value(env_value)
        except KeyError:
            raise KeyError(f"Environment variable '{name}' not found.")
        except Exception as e:
            raise ValueError(f"Error casting environment variable '{name}': {e}")
    
    @classmethod
    def _cast_value(cls, value: str) -> E:
        """Cast the string value from environment to the target type."""
        if cls._type_hint == str:
            return cast(E, value)
        else:
            # if type hint is not str, use the type constructor directly and let it throw natural errors
            constructor: Any = cls._type_hint
            return cast(E, constructor(value))


def ENV_Field(name: str, t: Type[E]) -> E:
    """An Environment variable field for Pydantic models.

    Returns a Pydantic Field that fetches its default value from an environment variable. 
    The Field will be excluded from model serialization.
    
    Example::

        some_env: str = ENV_Field('SOME_ENV_VAR', t=str)
    
    """
    return Field(default_factory=lambda: ENV[t](name), exclude=True)
