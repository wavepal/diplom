from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from index.models import *
import json
import random
import string
from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from django.utils import timezone
import pytz

def update_score(request):
    choice_id = request.POST.get('choice_id')
    score = request.POST.get('score')

    try:
        choice = Choices.objects.get(id=choice_id)
        choice.scores = int(score)
        choice.save()
        return JsonResponse({'status': 'success'})
    except Choices.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Choice not found'})
    
    
def delete_forms(request):
    if request.method == 'DELETE':
        form_ids = request.POST.getlist('forms[]')
        return JsonResponse({'message': 'Forms deleted successfully'}, status=200)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)
    
def create_form(request):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))

    if request.method == "POST":
        data = json.loads(request.body)
        title = data["title"]
        code = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(30))
        choices = Choices(choice = "Вариант 1")
        choices.save()
        question = Questions(question_type = "multiple choice", question= "Без названия", required= False)
        question.save()
        question.choices.add(choices)
        question.save()
        form = Form(code = code, title = title, creator=request.user)
        form.save()
        form.questions.add(question)
        form.save()
        return JsonResponse({"message": "Success", "code": code})
    else:
        return render(request, 'error/404.html')

def edit_form(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    formInfo = Form.objects.filter(code=code).first()
    if not formInfo:
        return HttpResponseRedirect(reverse("404"))

    # Только админы и тренеры могут редактировать формы
    if not (request.user.is_admin() or request.user.is_trainer()):
        return HttpResponseRedirect(reverse("403"))
        
    med_centers = RegionMedCenter.objects.all().order_by('region', 'med_center')
    
    return render(request, "index/form/edit_form.html", {
        "code": code,
        "form": formInfo,
        "med_centers": med_centers
    })

def edit_title(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)

    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else: formInfo = formInfo[0]
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        if len(data["title"]) > 0:
            formInfo.title = data["title"]
            formInfo.save()
        else:
            formInfo.title = formInfo.title[0]
            formInfo.save()
        return JsonResponse({"message": "Success", "title": formInfo.title})

def edit_description(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)

    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else: formInfo = formInfo[0]
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        formInfo.description = data["description"]
        formInfo.save()
        return JsonResponse({"message": "Success", "description": formInfo.description})

def form_share(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code=code)
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else:
        formInfo = formInfo[0]
    return render(request, "index/form/form_share.html", {"form": formInfo})

def form_settings(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code=code)
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else:
        formInfo = formInfo[0] 
    return render(request, "index/form/form_settings.html", {"form": formInfo})

def form_colors(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code=code)
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else:
        formInfo = formInfo[0]
    return render(request, "index/form/form_colors.html", {"form": formInfo})

def edit_bg_color(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)

    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else: formInfo = formInfo[0]
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        formInfo.background_color = data["bgColor"]
        formInfo.save()
        return JsonResponse({"message": "Success", "bgColor": formInfo.background_color})

def edit_text_color(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)

    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else: formInfo = formInfo[0]
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        formInfo.text_color = data["textColor"]
        formInfo.save()
        return JsonResponse({"message": "Success", "textColor": formInfo.text_color})

def edit_setting(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code=code).first()

    if not formInfo:
        return HttpResponseRedirect(reverse("404"))
    
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
    
    if request.method == "POST":
        data = json.loads(request.body)
        formInfo.collect_email = data.get("collect_email", formInfo.collect_email)
        formInfo.authenticated_responder = data.get("authenticated_responder", formInfo.authenticated_responder)
        formInfo.confirmation_message = data.get("confirmation_message", formInfo.confirmation_message)
        formInfo.edit_after_submit = data.get("edit_after_submit", formInfo.edit_after_submit)
        formInfo.limit_ip = data.get("limit_ip", formInfo.limit_ip)
        formInfo.submit_limit = data.get("submit_limit", formInfo.submit_limit)
        formInfo.is_single_form = data.get("is_single_form", formInfo.is_single_form)
        formInfo.is_active = data.get("is_active", formInfo.is_active)
        formInfo.allow_med_center_choice = data.get("allow_med_center_choice", formInfo.allow_med_center_choice)
        formInfo.save()
        return JsonResponse({'message': "Success"})

def delete_form(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)

    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else: formInfo = formInfo[0]
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "DELETE":

        for i in formInfo.questions.all():
            for j in i.choices.all():
                j.delete()
            i.delete()
        for i in Responses.objects.filter(response_to = formInfo):
            for j in i.response.all():
                j.delete()
            i.delete()
        formInfo.delete()
        return JsonResponse({'message': "Success"})

def edit_question(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    form_info = Form.objects.filter(code=code).first()

    if not form_info:
        return HttpResponseRedirect(reverse('404'))
    
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            question_id = data.get("id")
            question = Questions.objects.filter(id=question_id).first()
            
            if not question:
                return HttpResponseRedirect(reverse("404"))
            
            # Проверяем, изменился ли тип вопроса
            new_question_type = data.get("question_type")
            if new_question_type and new_question_type != question.question_type:
                # Если тип изменился, удаляем все ответы на этот вопрос
                from index.models import Answer
                Answer.objects.filter(answer_to=question).delete()
                
                # Удаляем все варианты ответов, если они были
                if question.choices.exists():
                    question.choices.all().delete()
                
                # Сбрасываем max_value для range slider
                if new_question_type == "range slider":
                    question.max_value = 100  # Устанавливаем значение по умолчанию
                else:
                    question.max_value = None
            
            question.question = data.get("question", question.question)
            question.question_type = new_question_type or question.question_type
            question.required = data.get("required", question.required)
            question.is_list = data.get("is_list", question.is_list)
            question.is_skip = data.get("is_skip", question.is_skip)
            question.is_negative = data.get("is_negative", question.is_negative)
            if "score" in data:
                question.score = data["score"]
            if "answer_key" in data:
                question.answer_key = data["answer_key"]
            
            question.save()
            
            return JsonResponse({'message': "Success"})
        
        except json.JSONDecodeError as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def edit_choice(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        choice_id = data["id"]
        choice = Choices.objects.filter(id = choice_id)
        if choice.count() == 0:
            return HttpResponseRedirect(reverse("404"))
        else: choice = choice[0]
        choice.choice = data["choice"]
        if(data.get('is_answer')): choice.is_answer = data["is_answer"]
        choice.save()
        return JsonResponse({'message': "Success"})


def add_choice(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    form_info = Form.objects.filter(code=code)

    if form_info.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        form_info = form_info[0]

    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))

    if request.method == "POST":
        data = json.loads(request.body)
        if "question" not in data:
            return JsonResponse({"error": "Question ID is required"}, status=400)
        choice_number = form_info.questions.get(pk=data["question"]).choices.count() + 1
        choice_text = f"Вариант {choice_number}"

        choice = Choices(choice=choice_text)
        choice.save()

        form_info.questions.get(pk=data["question"]).choices.add(choice)
        form_info.save()

        return JsonResponse({"message": "Success", "choice": choice.choice, "id": choice.id})

def remove_choice(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        choice = Choices.objects.filter(pk = data["id"])
        if choice.count() == 0:
            return HttpResponseRedirect(reverse("404"))
        else: choice = choice[0]
        choice.delete()
        return JsonResponse({"message": "Success"})

def get_choice(request, code, question):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "GET":
        question = Questions.objects.filter(id = question)
        if question.count() == 0: return HttpResponseRedirect(reverse('404'))
        else: question = question[0]
        choices = question.choices.all()
        choices = [{"choice":i.choice, "is_answer":i.is_answer, "id": i.id} for i in choices]
        return JsonResponse({"choices": choices, "question": question.question, "question_type": question.question_type, "question_id": question.id})

from django.db.models import Max

def add_question(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        # Получаем максимальный существующий order
        max_order = formInfo.questions.aggregate(Max('order'))['order__max']
        new_order = (max_order or -1) + 1  # Если вопросов нет, начинаем с 0
        
        choices = Choices(choice = "Вариант 1")
        choices.save()
        question = Questions(
            question_type = "multiple choice", 
            question = "Без названия", 
            required = False,
            is_list = False,
            is_skip = False,
            is_negative = False,
            max_value = 100,
            order = new_order
        )
        question.save()
        question.choices.add(choices)
        question.save()
        formInfo.questions.add(question)
        formInfo.save()
        return JsonResponse({
            'question': {
                'id': question.id,
                'question': question.question,
                'question_type': question.question_type,
                'required': question.required,
                'is_list': question.is_list,
                'is_skip': question.is_skip,
                'is_negative': question.is_negative,
                'max_value': question.max_value,
                'order': question.order
            },
            'choices': [{
                'id': choices.id,
                'choice': choices.choice,
                'is_answer': choices.is_answer
            }]
        })

def delete_question(request, code, question):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    # Получаем форму по коду
    formInfo = Form.objects.filter(code=code).first()
    if not formInfo:
        return HttpResponseRedirect(reverse('404'))

    # Проверка прав пользователя
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))

    if request.method == "DELETE":
        # Получаем вопрос по ID
        question = Questions.objects.filter(id=question).first()
        if not question:
            return HttpResponseRedirect(reverse("404"))

        # Удаляем связанные варианты выбора
        question.choices.all().delete()

        # Удаляем сам вопрос
        question.delete()

        return JsonResponse({"message": "Success"})

def copy_question(request, code, question):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    formInfo = Form.objects.filter(code=code).first()
    if not formInfo:
        return HttpResponseRedirect(reverse('404'))

    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))

    if request.method == "POST":
        # Получаем исходный вопрос
        source_question = Questions.objects.filter(id=question).first()
        if not source_question:
            return HttpResponseRedirect(reverse("404"))

        # Получаем максимальный существующий order
        max_order = formInfo.questions.aggregate(Max('order'))['order__max']
        new_order = (max_order or -1) + 1

        # Создаем новый вопрос с теми же параметрами
        new_question = Questions.objects.create(
            question_type=source_question.question_type,
            question=source_question.question,
            required=source_question.required,
            is_list=source_question.is_list,
            is_skip=source_question.is_skip,
            is_negative=source_question.is_negative,
            score=source_question.score,
            answer_key=source_question.answer_key,
            feedback=source_question.feedback,
            max_value=source_question.max_value,
            order=new_order
        )

        # Копируем варианты ответов, если они есть
        choices = []
        if source_question.choices.exists():
            for choice in source_question.choices.all():
                new_choice = Choices.objects.create(
                    choice=choice.choice,
                    is_answer=choice.is_answer,
                    scores=choice.scores
                )
                new_question.choices.add(new_choice)
                choices.append({
                    'id': new_choice.id,
                    'choice': new_choice.choice,
                    'is_answer': new_choice.is_answer
                })

        # Добавляем вопрос к форме
        formInfo.questions.add(new_question)

        return JsonResponse({
            'question': {
                'id': new_question.id,
                'question': new_question.question,
                'question_type': new_question.question_type,
                'required': new_question.required,
                'is_list': new_question.is_list,
                'is_skip': new_question.is_skip,
                'is_negative': new_question.is_negative,
                'max_value': new_question.max_value,
                'order': new_question.order
            },
            'choices': choices
        })

# def score(request, code):
#     if not request.user.is_authenticated:
#         return HttpResponseRedirect(reverse("login"))
#     formInfo = Form.objects.filter(code = code)
#     if formInfo.count() == 0:
#         return HttpResponseRedirect(reverse('404'))
#     else: formInfo = formInfo[0]
#     if not request.user.is_superuser:
#         return HttpResponseRedirect(reverse("403"))
#     if not formInfo.is_quiz:
#         return HttpResponseRedirect(reverse("edit_form", args = [code]))
#     else:
#         return render(request, "index/form/score.html", {
#             "form": formInfo
#         })

# def edit_score(request, code):
#     if not request.user.is_authenticated:
#         return HttpResponseRedirect(reverse("login"))
#     formInfo = Form.objects.filter(code = code)
#     if formInfo.count() == 0:
#         return HttpResponseRedirect(reverse('404'))
#     else: formInfo = formInfo[0]
#     if not request.user.is_superuser:
#         return HttpResponseRedirect(reverse("403"))
#     if not formInfo.is_quiz:
#         return HttpResponseRedirect(reverse("edit_form", args = [code]))
#     else:
#         if request.method == "POST":
#             data = json.loads(request.body)
#             question_id = data["question_id"]
#             question = formInfo.questions.filter(id = question_id)
#             if question.count() == 0:
#                 return HttpResponseRedirect(reverse("edit_form", args = [code]))
#             else: question = question[0]
#             score = data["score"]
#             if score == "": score = 0
#             question.score = score
#             question.save()
#             return JsonResponse({"message": "Success"})

# def answer_key(request, code):
#     if not request.user.is_authenticated:
#         return HttpResponseRedirect(reverse("login"))
#     formInfo = Form.objects.filter(code = code)
#     if formInfo.count() == 0:
#         return HttpResponseRedirect(reverse('404'))
#     else: formInfo = formInfo[0]
#     if not request.user.is_superuser:
#         return HttpResponseRedirect(reverse("403"))
#     if not formInfo.is_quiz:
#         return HttpResponseRedirect(reverse("edit_form", args = [code]))
#     else:
#         if request.method == "POST":
#             data = json.loads(request.body)
#             question = Questions.objects.filter(id = data["question_id"])
#             if question.count() == 0: return HttpResponseRedirect(reverse("edit_form", args = [code]))
#             else: question = question[0]
#             if question.question_type == "short" or question.question_type == "paragraph" or question.question_type == "range slider":
#                 question.answer_key = data["answer_key"]
#                 question.save()
#             else:
#                 for i in question.choices.all():
#                     i.is_answer = False
#                     i.save()
#                 if question.question_type == "multiple choice":
#                     choice = question.choices.get(pk = data["answer_key"])
#                     choice.is_answer = True
#                     choice.save()
#                 else:
#                     for i in data["answer_key"]:
#                         choice = question.choices.get(id = i)
#                         choice.is_answer = True
#                         choice.save()
#                 question.save()
#             return JsonResponse({'message': "Success"})

# def feedback(request, code):
#     if not request.user.is_authenticated:
#         return HttpResponseRedirect(reverse("login"))
#     formInfo = Form.objects.filter(code = code)

#     if formInfo.count() == 0:
#         return HttpResponseRedirect(reverse('404'))
#     else: formInfo = formInfo[0]
#     if not request.user.is_superuser:
#         return HttpResponseRedirect(reverse("403"))
#     if not formInfo.is_quiz:
#         return HttpResponseRedirect(reverse("edit_form", args = [code]))
#     else:
#         if request.method == "POST":
#             data = json.loads(request.body)
#             question = formInfo.questions.get(id = data["question_id"])
#             question.feedback = data["feedback"]
#             question.save()
#             return JsonResponse({'message': "Success"})

def view_form(request, code):
    formInfo = Form.objects.filter(code=code).first()
    if not formInfo:
        return HttpResponseRedirect(reverse("404"))

    # Руководители не могут заполнять формы
    if request.user.is_authenticated and request.user.is_manager():
        return HttpResponseRedirect(reverse("responses", args=[code]))
    
    # Получаем список медцентров, если форма разрешает выбор медцентра
    med_centers = None
    if formInfo.allow_med_center_choice:
        med_centers = RegionMedCenter.objects.all().order_by('region', 'med_center')
    else:
        # Для админов всегда загружаем список медцентров
        if request.user.is_authenticated and request.user.is_superuser:
            med_centers = RegionMedCenter.objects.all().order_by('region', 'med_center')
    
    return render(request, "index/form/view_form.html", {
        "form": formInfo,
        "med_centers": med_centers
    })

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

from datetime import datetime, date, time
from django.utils import timezone
import pytz

def submit_form(request, code):
    formInfo = Form.objects.filter(code=code).first()
    
    if not formInfo:
        return HttpResponseRedirect(reverse('404'))
    
    if formInfo.authenticated_responder and not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    if request.method == "POST":
        client_ip = get_client_ip(request)
        
        # Проверяем ограничения IP и лимиты отправки
        if formInfo.limit_ip:
            existing_response = Responses.objects.filter(response_to=formInfo, responder_ip=client_ip).order_by('-createdAt').first()
            if existing_response and datetime.now() - existing_response.createdAt < timedelta(hours=24):
                return render(request, "index/form/form_response.html", {
                    "form": formInfo,
                    "message": "Вы уже отправили ответ на эту форму в последние 24 часа."
                })

        if formInfo.submit_limit:
            existing_response = Responses.objects.filter(response_to=formInfo, responder=request.user).order_by('-createdAt').first()
            if existing_response and timezone.now() - existing_response.createdAt < timedelta(hours=24):
                return render(request, "index/form/form_response.html", {
                    "form": formInfo,
                    "message": "Вы уже отправили ответ на эту форму в последние 24 часа."
                })
        
        response_code = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(20))
        
        if request.user.is_authenticated:
            # Получаем пользовательские данные
            custom_email = request.POST.get("custom_email")
            custom_gender = request.POST.get("custom_gender")
            custom_city = request.POST.get("custom_city")
            custom_med = request.POST.get("custom_med")
            custom_birth_date = request.POST.get("custom_birth_date")
            custom_username = request.POST.get("custom_username")
            custom_submit_date = request.POST.get("custom_submit_date")
            custom_submit_time = request.POST.get("custom_submit_time")
            
            # Проверяем, выбрал ли пользователь медцентр
            med_center_choice = request.POST.get("med_center_choice")

            # Создаем базовый объект response БЕЗ сохранения
            response = Responses(
                response_code=response_code,
                response_to=formInfo,
                responder_ip=client_ip,
                responder=request.user
            )

            # Устанавливаем пользовательские данные
            response.responder_email = custom_email if custom_email else request.user.email
            response.responder_gender = custom_gender if custom_gender else (request.user.gender if hasattr(request.user, 'gender') else None)
            response.responder_city = custom_city if custom_city else (request.user.city if hasattr(request.user, 'city') else None)
            
            # Приоритет: 1) custom_med от админа, 2) med_center_choice от пользователя, 3) med_center пользователя
            if custom_med:
                response.responder_med = custom_med
            elif formInfo.allow_med_center_choice and med_center_choice:
                response.responder_med = med_center_choice
            else:
                response.responder_med = request.user.med_center if hasattr(request.user, 'med_center') else None
                
            response.responder_birth_date = custom_birth_date if custom_birth_date else (request.user.date_of_birth if hasattr(request.user, 'date_of_birth') else None)
            response.responder_username = custom_username if custom_username else request.user.username

            # Устанавливаем пользовательскую дату и время отправки
            if custom_submit_date and custom_submit_time:
                try:
                    submit_date = datetime.strptime(custom_submit_date, '%Y-%m-%d').date()
                    submit_time = datetime.strptime(custom_submit_time, '%H:%M').time()
                    custom_datetime = datetime.combine(submit_date, submit_time)
                    tz = pytz.timezone('Asia/Yekaterinburg')
                    # Заменяем прямую локализацию на более безопасный метод
                    aware_datetime = timezone.make_aware(custom_datetime, timezone=tz)
                    response.createdAt = aware_datetime
                except (ValueError, TypeError):
                    response.createdAt = timezone.now()
            else:
                response.createdAt = timezone.now()

            # Вычисляем возраст на основе даты рождения
            if response.responder_birth_date:
                today = datetime.now().date()
                birthdate = datetime.strptime(str(response.responder_birth_date), '%Y-%m-%d').date()
                response.responder_age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

            # Теперь сохраняем объект response
            response.save()

        elif request.user.is_authenticated and formInfo.authenticated_responder:
            response = Responses(
                response_code=response_code,
                response_to=formInfo,
                responder_ip=client_ip,
                responder=request.user
            )
            
            # Проверяем, выбрал ли пользователь медцентр
            if formInfo.allow_med_center_choice and request.POST.get("med_center_choice"):
                response.responder_med = request.POST.get("med_center_choice")
                
            response.save()
        elif formInfo.collect_email:
            response = Responses(
                response_code=response_code,
                response_to=formInfo,
                responder_ip=client_ip,
                responder_email=request.POST.get("email-address")
            )
            
            # Проверяем, выбрал ли пользователь медцентр
            if formInfo.allow_med_center_choice and request.POST.get("med_center_choice"):
                response.responder_med = request.POST.get("med_center_choice")
                
            response.save()
        else:
            # Для анонимных пользователей
            response = Responses(
                response_code=response_code,
                response_to=formInfo,
                responder_ip=client_ip
            )
            
            # Проверяем, выбрал ли пользователь медцентр
            if formInfo.allow_med_center_choice and request.POST.get("med_center_choice"):
                response.responder_med = request.POST.get("med_center_choice")
                
            response.save()

        # Сохраняем ответы на вопросы
        if 'response' in locals():  # Проверяем, что переменная response существует
            for i in request.POST:
                if i in ["csrfmiddlewaretoken", "email-address", "custom_email", "custom_gender", 
                        "custom_city", "custom_med", "custom_birth_date", "custom_username",
                        "custom_submit_date", "custom_submit_time", "med_center_choice"] or i.startswith("is_skipped_"):
                    continue
                
                try:
                    question_id = int(i)
                except ValueError:
                    continue
                
                question = formInfo.questions.get(id=question_id)
                for j in request.POST.getlist(i):
                    is_skipped = request.POST.get(f'is_skipped_{question.id}') == 'True'
                    answer = Answer(answer=j, answer_to=question, is_skipped=is_skipped)
                    answer.save()
                    response.response.add(answer)

            response.save()
            return render(request, "index/form/form_response.html", {
                "form": formInfo,
                "response": response
            })
        else:
            # Если по какой-то причине response не создан, возвращаем страницу без него
            return render(request, "index/form/form_response.html", {
                "form": formInfo,
                "message": "Ваш ответ был получен, но произошла ошибка при сохранении деталей ответа."
            })
    
def form_list_view(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    if request.method == 'POST':
        selected_forms = request.POST.getlist('selected_forms[]')
        if selected_forms and request.user.is_admin():  # Только админы могут удалять формы
            Form.objects.filter(id__in=selected_forms).delete()

    forms = Form.objects.all()
    return render(request, 'index/form/form_list.html', {'forms': forms})

@csrf_exempt  # Добавляем декоратор, если его нет
def update_max_value(request, question_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    if request.method == 'POST':
        try:
            question = Questions.objects.get(pk=question_id)
            data = json.loads(request.body)
            max_value = data.get('max_value')
            
            if max_value is not None:
                try:
                    max_value = int(max_value)  # Убедимся, что значение целое число
                    question.max_value = max_value
                    question.save()
                    return JsonResponse({'message': 'Max value updated successfully', 'max_value': max_value})
                except ValueError:
                    return JsonResponse({'error': 'Invalid max value format'}, status=400)
            else:
                return JsonResponse({'error': 'Max value not provided'}, status=400)
                
        except Questions.DoesNotExist:
            return JsonResponse({'error': 'Question not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def update_question_order(request, code):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse({"error": "Unauthorized"}, status=403)
        
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question_orders = data.get("questionOrders", [])
            
            # Получаем форму
            form = Form.objects.get(code=code)
            
            # Обновляем порядок для каждого вопроса
            for order_data in question_orders:
                question_id = order_data.get("id")
                new_order = order_data.get("order")
                
                # Проверяем, что вопрос принадлежит этой форме
                if form.questions.filter(id=question_id).exists():
                    question = Questions.objects.get(id=question_id)
                    question.order = new_order
                    question.save()
            
            return JsonResponse({"message": "Success"})
        except Form.DoesNotExist:
            return JsonResponse({"error": "Form not found"}, status=404)
        except Exception as e:
            print(f"Error updating question order: {str(e)}")  # Для отладки
            return JsonResponse({"error": str(e)}, status=400)
            
    return JsonResponse({"error": "Method not allowed"}, status=405)