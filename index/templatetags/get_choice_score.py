from django import template
from django.shortcuts import get_object_or_404
from index.models import Responses, Choices

register = template.Library()

@register.filter
def get_score_choice(response, question):
    score = 0
    response_obj = get_object_or_404(Responses, response_code=response.response_code)
    for resp in response_obj.response.filter(answer_to_id=question.pk):
        if question.question_type == "multiple choice":
            choice = get_object_or_404(Choices, pk=resp.answer)
            score += choice.scores
        elif question.question_type == "checkbox":
            for choice in question.choices.filter(pk=resp.answer):
                score += choice.scores
    return score

@register.filter
def total_score(response, question):
    score = 0
    response_obj = get_object_or_404(Responses, response_code=response.response_code)

    if question.question_type in ["short", "paragraph", "range slider"]:
        if response_obj.response.filter(answer_to=question, answer=question.answer_key).exists():
            score += question.score
    elif question.question_type == "multiple choice":
        answer_key = None
        for choice in question.choices.all():
            if choice.is_answer:
                answer_key = choice.id
        for resp in response_obj.response.filter(answer_to=question):
            if answer_key is not None and int(answer_key) == int(resp.answer):
                score += question.score
            choice = get_object_or_404(Choices, pk=resp.answer)
            score += choice.scores
    elif question.question_type == "checkbox":
        selected_answers = set()
        correct_answers = set()
        for resp in response_obj.response.filter(answer_to=question):
            selected_answers.add(int(resp.answer))
        for choice in question.choices.all():
            if choice.is_answer:
                correct_answers.add(choice.pk)
        if selected_answers == correct_answers:
            score += question.score
        for answer_id in selected_answers:
            choice = get_object_or_404(Choices, pk=answer_id)
            score += choice.scores
    return score