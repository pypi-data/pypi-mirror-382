# The 'prefixes' tuple contains the current object name prefixes.
# When defining styles, avoid using object names as keys.
# For example, a structure like Grid: { chart: { } }
# will cause issues, because chart is also an object name.

prefixes = (
    "chart.",
    "grid.",
    "report.",
    "chapter.",
    "table.",
    "text.",
)

def flatten_dict(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def add_prefix_to_styles(obj_name, styles):
    flatten_styles = flatten_dict(styles)
    return {
        key if key.startswith(prefixes) else f"{obj_name}.{key}": value
        for key, value in flatten_styles.items()
    }
