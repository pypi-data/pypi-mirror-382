import inspect

from rephorm.object_params.settings import object_params

def validate_kwargs(func):
    """
    A decorator that validates kwargs (keys and values).
    It uses ultimate_setting_owner dict!
    """
    def wrapper(*args, **kwargs):
        module_name = func.__module__.split('.')[-1].upper()

        signature = inspect.signature(func)
        excluded_keys = set(signature.parameters.keys())

        for key, value in kwargs.items():

            # Skip validation for object args/params (We want to validate only kwargs)
            if key in excluded_keys and key not in object_params:
                continue

            # Validate key | If the key is within object_params (allowed keys)
            if key not in object_params:
                raise KeyError(f"{module_name}: Invalid key '{key}'. "
                               f"Allowed keys are: {list(object_params.keys())}")

            # Get the expected type from ultimate_setting_owner
            expected_type = object_params[key]["type"]
            object_params_key = object_params[key]

            # Validate value type
            # to skip type-checking for complex types
            if expected_type is None:
                continue
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"{module_name}: Argument '{key}' must be of type {expected_type.__name__}, "
                    f"got {type(value).__name__} instead."
                )

            # Validate possible values | if they are defined within the object_params
            if "possible_values" in object_params_key and value not in object_params_key["possible_values"]:
                possible_values = object_params_key["possible_values"]
                raise ValueError(
                    f"{module_name}: Argument '{key}' has invalid value '{value}'. Allowed values are: {possible_values}")

        return func(*args, **kwargs)

    return wrapper