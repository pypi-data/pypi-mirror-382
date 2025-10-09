import copy

from rephorm.dict.styles import default_styles

# Get the allowed Styles structure from default_styles
allowed_structure = default_styles()

def validate_value_type(obj_name, path, value, structure=allowed_structure):
    keys = path.split('.')
    final_structure = structure
    current_path = []

    for key in keys:
        current_path.append(key)
        if isinstance(final_structure, dict):
            if key not in final_structure:
                raise KeyError(f"({obj_name} object): Styles key '{key}' for '{'.'.join(current_path[:-1])}' does not exist. "
                               f"Available keys at this level: {list(final_structure.keys())}")
            final_structure = final_structure.get(key, {})
        else:
            # If we've reached a non-dictionary node, we can't go further; this means wrong nesting
            raise KeyError(f"Styles: Invalid path '{path}'. No further nesting allowed under '{keys[-2]}'.")

    if isinstance(final_structure, dict):
        if not isinstance(value, dict):
            available_keys = list(final_structure.keys())
            raise ValueError(
                f"Styles key error: '{path}' expects a dictionary with keys: {available_keys}. Got {type(value).__name__} instead.")
        else:
            # Recursively validate each sub-key for dictionaries
            for sub_key, sub_value in value.items():
                new_path = f"{path}.{sub_key}"
                validate_value_type(obj_name, new_path, sub_value)
    else:
        # Skips type validation if the type of Final structure's (edge parameter in default_styles)
        # value was set to None.
        if type(final_structure) is type(None):
            return

        expected_type = type(final_structure) if not isinstance(final_structure, type) else final_structure

        if not isinstance(value, expected_type) and not (isinstance(value, (int, float)) and expected_type in (int, float)):
            raise TypeError(
                f"Styles: Invalid type for '{path}': Expected {expected_type.__name__}, got {type(value).__name__}")

def create_nested_structure(obj_name, flat_dict):

    if flat_dict is None:
        return flat_dict

    nested_dict = {}

    flat_dict = copy.deepcopy(flat_dict)

    for key, value in flat_dict.items():
        validate_value_type(obj_name, key, value, allowed_structure)
        keys = key.split(".")
        d = nested_dict

        for k in keys[:-1]:
            d = d.setdefault(k, {})

        d[keys[-1]] = value

    return nested_dict

def update_nested_structure(org_dict, new_dict):
    if new_dict is None:
        return org_dict

    result = copy.deepcopy(org_dict)

    for key, value in new_dict.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = update_nested_structure(result[key], value)
        else:
            result[key] = value

    return result