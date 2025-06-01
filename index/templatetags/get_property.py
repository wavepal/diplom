from django import template
register = template.Library()

@register.filter
def get_property(array, index):
    if array is None:
        return None
    return array[index]

@register.filter
def get_dict_item(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(str(key), None)

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(key, None)

@register.filter
def get_dict_items(dictionary, key=None):
    if dictionary is None:
        return []
    
    if key is not None:
        try:
            sub_dict = dictionary.get(key, {})
            if isinstance(sub_dict, dict):
                return sub_dict.items()
            return []
        except:
            return []
    
    try:
        if isinstance(dictionary, dict):
            return dictionary.items()
        return []
    except:
        return []