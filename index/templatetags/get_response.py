from django import template
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()

@register.filter
def get_response(responses, pk):
    try:
        return responses.response.get(answer_to__pk=pk).answer
    except ObjectDoesNotExist:
        return None
    
@register.filter
def get_skip(responses, pk):
    try:
        return responses.response.get(answer_to__pk=pk).is_skipped
    except ObjectDoesNotExist:
        return None