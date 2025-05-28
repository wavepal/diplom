from django import template
from django.shortcuts import get_object_or_404
from index.models import Choices

register = template.Library()

@register.filter
def get_choice_by_id(choices, choice_id):
    try:
        return choices.filter(id=choice_id).first()
    except (ValueError, AttributeError):
        return None

@register.filter
def get_answer(answers, question):
    """Get the answer for a specific question from a list of answers."""
    try:
        return answers.filter(answer_to=question).first()
    except (ValueError, AttributeError):
        return None 