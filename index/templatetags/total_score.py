from django import template

register = template.Library()

@register.filter
def total_possible_score(question):
    if question.question_type == "multiple choice":
        max_choice_score = max([choice.scores for choice in question.choices.all()])
        return max_choice_score + question.score
    elif question.question_type == "checkbox":
        choices_total_score = sum([choice.scores for choice in question.choices.all()])
        return choices_total_score + question.score
    else:
        return question.score