from django import template
from django.shortcuts import get_object_or_404
from index.models import Responses, Choices

register = template.Library()

@register.filter
def calculate_score(response, form):
    score = 0
    response_obj = get_object_or_404(Responses, response_code=response.response_code)
    _temp = []

    for resp in response_obj.response.all():
        question = resp.answer_to
        if question.question_type in ["short", "paragraph", "range slider"]:
            if resp.answer == question.answer_key:
                score += question.score
        elif question.question_type == "multiple choice":
            choice_score = 0
            for choice in question.choices.all():
                if choice.id == int(resp.answer):
                    choice_score = choice.scores
                if choice.is_answer and choice.id == int(resp.answer):
                    score += question.score
            score += choice_score
        elif question.question_type == "checkbox" and question.pk not in _temp:
            answers = []
            answer_keys = []
            selected_scores_sum = 0
            for resp in response_obj.response.filter(answer_to__pk=question.pk):
                answers.append(int(resp.answer))
                for choice in resp.answer_to.choices.all():
                    if choice.is_answer and choice.pk not in answer_keys:
                        answer_keys.append(choice.pk)
                    if choice.pk == int(resp.answer):
                        selected_scores_sum += choice.scores
                _temp.append(question.pk)
            if set(answers) == set(answer_keys):
                score += question.score
            score += selected_scores_sum
    return score

@register.filter
def calculate_total_score(form):
    total_score = 0
    for question in form.questions.all():
        if question.question_type == "multiple choice":
            choices = question.choices.all()
            max_choice_score = max([choice.scores for choice in choices]) if choices else 0
            total_score += max_choice_score + question.score
        elif question.question_type == "checkbox":
            choices_total_score = sum([choice.scores for choice in question.choices.all()])
            total_score += choices_total_score + question.score
        else:
            total_score += question.score
    return total_score