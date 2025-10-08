from typing import Any


def remove_underscore_from_dict_keys(data: Any) -> Any:
    """
    Recursively rename dictionary keys by replacing '_$' with '$' only when it starts the key.
    
    Args:
        data: The data structure to process (dict, list, or other)
    
    Returns:
        The data structure with renamed keys
    """
    if isinstance(data, dict):
        # Create a new dictionary with renamed keys
        new_dict = {}
        for key, value in data.items():
            # Replace '_$' with '$' only if the key starts with '_$'
            if isinstance(key, str) and key.startswith("_$"):
                new_key = key[1:]  # Remove the first character '_'
            else:
                new_key = key
            # Recursively process the value
            new_dict[new_key] = remove_underscore_from_dict_keys(value)
        return new_dict
    elif isinstance(data, list):
        # Process each item in the list
        return [remove_underscore_from_dict_keys(item) for item in data]
    else:
        # Return primitive values as-is
        return data


def add_underscore_to_dict_keys(data: Any) -> Any:
    """
    Recursively rename dictionary keys by adding '_' before '$' only when the key starts with '$'.
    
    Args:
        data: The data structure to process (dict, list, or other)
    
    Returns:
        The data structure with renamed keys
    """
    if isinstance(data, dict):
        # Create a new dictionary with renamed keys
        new_dict = {}
        for key, value in data.items():
            # Add '_' before '$' only if the key starts with '$'
            if isinstance(key, str) and key.startswith("$"):
                new_key = "_" + key  # Add underscore before the dollar sign
            else:
                new_key = key
            # Recursively process the value
            new_dict[new_key] = add_underscore_to_dict_keys(value)
        return new_dict
    elif isinstance(data, list):
        # Process each item in the list
        return [add_underscore_to_dict_keys(item) for item in data]
    else:
        # Return primitive values as-is
        return data