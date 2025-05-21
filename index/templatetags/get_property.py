from django import template
register = template.Library()

@register.filter
def get_property(array, index):
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