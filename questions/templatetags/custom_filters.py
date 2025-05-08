from django import template
import random

register = template.Library()

@register.filter
def shuffle(arg):
    tmp = list(arg)[:]
    random.shuffle(tmp)
    return tmp

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)