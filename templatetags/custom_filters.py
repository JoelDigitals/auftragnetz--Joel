from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Ermöglicht dictionary[key] im Template"""
    return dictionary.get(key)