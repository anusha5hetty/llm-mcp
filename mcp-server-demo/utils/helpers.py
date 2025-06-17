def find_details_in_dct(payload, key, value):
    for item in payload:
        if item.get(key) == value:
            return item
        
def is_string_json(str_value):
    return str_value.startswith("{") and str_value.endswith("}") or str_value.startswith("[") and str_value.endswith("]")