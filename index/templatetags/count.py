from django import template
from django.shortcuts import render, get_object_or_404
from index.models import Choices
register = template.Library()

@register.filter
def count(array):
    return len(array)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_choice(choices, choice_id):
    return choices.filter(id=choice_id).first()

@register.filter
def get_choice_scores(choice):
    return choice.scores

@register.filter
def in_list(value, arg):
    return value in arg.split(',')