from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using bracket notation."""
    if dictionary is None:
        return None
    return dictionary.get(str(key)) if isinstance(dictionary, dict) else None 